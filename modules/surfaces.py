from core.bridge import execute_fusion_script, FusionBridgeError
from core.utils import format_response, register_tool
from core.error_handler import bridge_error_message, get_result_value, map_result_error, localized_error
from modules.surfaces_scripts import (
    build_edit_surfaces_script,
)

def edit_surfaces_logic(operations: list[dict], lang: str = "en"):
    """
    Executes multiple surface operations in a single batch.
    Supported actions: patch, offset, stitch, thicken.
    Each operation should be a dict with 'action' and required parameters.
    """
    try:
        res = execute_fusion_script(build_edit_surfaces_script(), {"operations": operations}, use_common=["find_body"])
        val = get_result_value(res)
        if "ERR_" in val:
            return f"Error: {val}"
        return format_response(lang, "surfaces_updated")
    except FusionBridgeError as e: return bridge_error_message(e)

def register_surface_tools(mcp):
    register_tool(mcp, "edit_surfaces", edit_surfaces_logic)
