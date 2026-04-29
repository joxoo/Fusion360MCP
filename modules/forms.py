from core.bridge import execute_fusion_script, FusionBridgeError
from core.utils import format_response, register_tool
from core.error_handler import bridge_error_message, get_result_value, localized_error, map_result_error
from modules.forms_scripts import (
    build_edit_forms_script,
)

def edit_forms_logic(operations: list[dict], lang: str = "en"):
    """
    Executes multiple T-Spline form operations in a single batch.
    Supported actions: extrude, set_display_mode, clear_symmetry, convert.
    Each operation should be a dict with 'action' and required parameters.
    """
    try:
        res = execute_fusion_script(build_edit_forms_script(), {"operations": operations}, use_common=["find_body"])
        val = get_result_value(res)
        if "ERR_" in val:
            return f"Error: {val}"
        return format_response(lang, "forms_updated")
    except FusionBridgeError as e: return bridge_error_message(e)

def register_form_tools(mcp):
    register_tool(mcp, "edit_forms", edit_forms_logic)
