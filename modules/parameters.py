from core.bridge import execute_fusion_script, FusionBridgeError
from core.utils import format_response, register_tool
from core.error_handler import (
    bridge_error_message,
    get_result_value,
    map_result_error,
    localized_error,
)
from modules.parameters_scripts import build_manage_parameter_script, build_list_parameters_script, build_delete_parameter_script
import json

def list_parameters_logic(lang: str = "en"):
    """Returns a list of all user parameters in the design."""
    try:
        res = execute_fusion_script(build_list_parameters_script())
        return get_result_value(res, "[]")
    except FusionBridgeError as e: return bridge_error_message(e)

def delete_parameter_logic(name: str, lang: str = "en"):
    """Deletes a user parameter by name."""
    try:
        res = execute_fusion_script(build_delete_parameter_script(), {"name": name})
        val = get_result_value(res)
        error_map = {
            "ERR_NOT_FOUND": f"Error: Parameter '{name}' not found.",
            "ERR_IN_USE": f"Error: Parameter '{name}' is currently in use and cannot be deleted.",
        }
        err = map_result_error(val, lang, error_map)
        if err: return err
        return f"Parameter '{name}' successfully deleted."
    except FusionBridgeError as e: return bridge_error_message(e)

def manage_parameter_logic(name: str, expression: str, unit: str = "mm", comment: str = "", lang: str = "en"):
    """Business logic to add or update a user parameter in Fusion 360."""
    try:
        res = execute_fusion_script(build_manage_parameter_script(), {
            "name": name, "expr": expression, "unit": unit, "comment": comment
        })
        val = get_result_value(res, "ERR_UNKNOWN")
        
        error_map = {
            "UPDATED": localized_error("parameter_updated", name=name),
        }
        # Special handling for "UPDATED" which is actually a success state in the old logic but treated as a code here
        if val == "UPDATED":
            return format_response(lang, "parameter_updated", name=name)
        
        if val.startswith("ERR_"):
            return format_response(lang, "parameter_error", val=val)
            
        return format_response(lang, "parameter_created", name=name)
    except FusionBridgeError as e: return bridge_error_message(e)

def register_parameter_tools(mcp):
    register_tool(mcp, "list_parameters", list_parameters_logic)
    register_tool(mcp, "delete_parameter", delete_parameter_logic)
    register_tool(mcp, "manage_parameter", manage_parameter_logic)
