from core.bridge import execute_fusion_script, FusionBridgeError
from core.utils import format_response, register_tool
from core.error_handler import (
    bridge_error_message,
    get_result_value,
    map_result_error,
)
from modules.parameters_scripts import (
    build_list_parameters_script,
    build_edit_parameters_script,
)
import json

def list_parameters_logic(lang: str = "en"):
    """Returns a list of all user parameters in the design."""
    try:
        res = execute_fusion_script(build_list_parameters_script())
        return get_result_value(res, "[]")
    except FusionBridgeError as e: return bridge_error_message(e)

def edit_parameters_logic(operations: list[dict], lang: str = "en"):
    """
    Executes multiple parameter operations in a single batch.
    Supported actions: set (create/update), delete.
    Each operation should be a dict with 'action' and required parameters.
    """
    try:
        res = execute_fusion_script(build_edit_parameters_script(), {"operations": operations})
        result_str = get_result_value(res, "OK")
        if "ERR" in result_str:
            return f"Error updating parameters: {result_str}"
        return format_response(lang, "parameters_updated")
    except FusionBridgeError as e: return bridge_error_message(e)

def register_parameter_tools(mcp):
    register_tool(mcp, "list_parameters", list_parameters_logic)
    register_tool(mcp, "edit_parameters", edit_parameters_logic)
