from core.bridge import execute_fusion_script, FusionBridgeError
from core.utils import format_response, register_tool
from core.error_handler import (
    bridge_error_message,
    get_result_value,
    map_result_error,
    localized_error,
)
from modules.mesh_scripts import (
    build_import_mesh_script,
    build_edit_mesh_script,
)

MESH_ERROR_MAP = {
    "ERR_NOT_A_MESH": "Error: Target is not a mesh body.",
    "ERR_BODY": localized_error("body_not_found"),
}

def import_mesh_logic(path: str, lang: str = "en"):
    """Imports an external mesh file (STL, OBJ)."""
    try:
        res = execute_fusion_script(build_import_mesh_script(), {"path": path})
        val = get_result_value(res)
        if val == "OK": return format_response(lang, "mesh_imported")
        return f"Error: {val}"
    except FusionBridgeError as e: return bridge_error_message(e)

def edit_mesh_logic(operations: list[dict], lang: str = "en"):
    """
    Executes multiple mesh operations in a single batch.
    Supported actions: remesh, smooth, repair, convert.
    Each operation should be a dict with 'action' and required parameters.
    """
    try:
        res = execute_fusion_script(build_edit_mesh_script(), {"operations": operations}, use_common=["find_body"])
        val = get_result_value(res)
        err = map_result_error(val, lang, MESH_ERROR_MAP)
        if err: return err
        return format_response(lang, "mesh_updated")
    except FusionBridgeError as e: return bridge_error_message(e)

def register_mesh_tools(mcp):
    register_tool(mcp, "import_mesh", import_mesh_logic)
    register_tool(mcp, "edit_mesh", edit_mesh_logic)
