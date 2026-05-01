from core.bridge import execute_fusion_script, FusionBridgeError
from core.utils import format_response, register_tool
from core.error_handler import (
    bridge_error_message,
    get_result_value,
)
from modules.design_scripts import (
    build_manage_design_script,
)
import json
from pathlib import Path

_TOOL_ACTION_GUIDE = None


def load_tool_action_guide() -> dict:
    global _TOOL_ACTION_GUIDE
    if _TOOL_ACTION_GUIDE is not None:
        return _TOOL_ACTION_GUIDE

    guide_path = Path(__file__).with_name("tool_action_guides.json")
    with guide_path.open("r", encoding="utf-8") as handle:
        _TOOL_ACTION_GUIDE = json.load(handle)
    return _TOOL_ACTION_GUIDE

def _reject_blocking_dialog_calls(script: str) -> str | None:
    blocked_markers = (
        "messageBox(",
        ".messageBox(",
        "inputBox(",
        ".inputBox(",
        "createFileDialog(",
        ".createFileDialog(",
    )
    if any(marker in script for marker in blocked_markers):
        return (
            "Error: direct_api_access scripts must not open Fusion UI dialogs "
            "(messageBox, inputBox, createFileDialog). Return data via returnValue "
            "or print() instead."
        )
    return None

def manage_design_logic(action: str = "cleanup", filename: str = "model", lang: str = "en"):
    """
    Handles design-level operations.
    Supported actions: cleanup, restart_mcp, create_new, export_step, export_stl.
    """
    try:
        res = execute_fusion_script(build_manage_design_script(), {
            "action": action, 
            "filename": filename
        })
        val = get_result_value(res)
        if val == "OK" or "Exported" in val:
            msg_map = {"cleanup": "design_cleaned", "restart_mcp": "mcp_restart_sent", "create_new": "document_created"}
            return format_response(lang, msg_map.get(action, "OK"))
        return f"Error: {val}"
    except FusionBridgeError as e: return bridge_error_message(e)

def direct_api_access_logic(script: str, lang: str = "en"):
    """Executes raw Python code directly in Fusion 360."""
    blocked_error = _reject_blocking_dialog_calls(script)
    if blocked_error:
        return blocked_error
    try:
        res = execute_fusion_script(script)
        data = res.get("data") or []
        if data:
            return "\n".join(str(item) for item in data)
        return res.get("detail") or "Script executed successfully with no output."
    except FusionBridgeError as e:
        return bridge_error_message(e)

_mcp_instance = None

async def list_mcp_tools_logic(lang: str = "en"):
    """Returns a list of all currently registered MCP tools and their descriptions."""
    global _mcp_instance
    if not _mcp_instance:
        return "Error: MCP instance not initialized."
    
    tools = await _mcp_instance.list_tools()
    report = ["Registered Fusion360 MCP Tools:"]
    for t in sorted(tools, key=lambda x: x.name):
        report.append(f"- {t.name}: {t.description}")
    return "\n".join(report)

def describe_tool_actions_logic(tool_name: str = "", lang: str = "en"):
    """
    Returns action guidance for the compact public API.
    Use this when the client is unsure which batch action or scope fields to send.
    """
    tool_action_guide = load_tool_action_guide()
    if tool_name:
        guide = tool_action_guide.get(tool_name)
        if not guide:
            return f"Error: No action guide found for tool '{tool_name}'."
        return json.dumps({tool_name: guide}, indent=2)
    return json.dumps(tool_action_guide, indent=2)

def register_design_tools(mcp):
    global _mcp_instance
    _mcp_instance = mcp
    
    register_tool(mcp, "manage_design", manage_design_logic)
    register_tool(mcp, "direct_api_access", direct_api_access_logic)
    register_tool(mcp, "list_mcp_tools", list_mcp_tools_logic)
    register_tool(mcp, "describe_tool_actions", describe_tool_actions_logic)
