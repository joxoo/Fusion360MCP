from core.bridge import execute_fusion_script, FusionBridgeError
from core.utils import format_response, register_tool
from modules.design_scripts import (
    build_cleanup_design_script,
    build_create_new_design_script,
    build_restart_mcp_script,
)

def cleanup_design_logic(lang: str = "en"):
    """Unifies cleanup logic for both DE and EN."""
    try:
        res = execute_fusion_script(build_cleanup_design_script())
        val = res.get("data", ["Error"])[0]
        if val == "OK":
            return format_response(lang, "design_cleaned")
        return val
    except FusionBridgeError as e: return f"Error: {str(e)}"

def restart_mcp_logic(lang: str = "en"):
    """Manually restarts the MCP server subprocess."""
    try:
        execute_fusion_script(build_restart_mcp_script())
        return format_response(lang, "mcp_restart_sent")
    except FusionBridgeError as e: return f"Error: {str(e)}"

def create_new_design_logic(lang: str = "en"):
    """Creates a new empty Fusion 360 document."""
    try:
        if execute_fusion_script(build_create_new_design_script()):
            return format_response(lang, "document_created")
        return "Error creating document."
    except FusionBridgeError as e: return f"Error: {str(e)}"

def change_design_mode_logic(mode: str = "Assembly", lang: str = "en"):
    """Switch mode between 'Part' and 'Assembly'."""
    return format_response(lang, "mode_changed")

def direct_api_access_logic(script: str, lang: str = "en"):
    """Executes raw Python code directly in Fusion 360."""
    try:
        res = execute_fusion_script(script)
        data = res.get("data") or []
        return "\n".join(str(item) for item in data) if data else "OK"
    except FusionBridgeError as e:
        return f"Error: {str(e)}"

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

def register_design_tools(mcp):
    global _mcp_instance
    _mcp_instance = mcp
    
    register_tool(mcp, "direct_api_access", direct_api_access_logic)
    register_tool(mcp, "list_mcp_tools", list_mcp_tools_logic)
    register_tool(mcp, "cleanup_design", cleanup_design_logic)
    register_tool(mcp, "restart_mcp", restart_mcp_logic)
    register_tool(mcp, "create_new_design", create_new_design_logic)
    register_tool(mcp, "change_design_mode", change_design_mode_logic)
