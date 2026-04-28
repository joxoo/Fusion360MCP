from core.bridge import execute_fusion_script, FusionBridgeError
from core.utils import format_response, register_tool
from core.error_handler import (
    bridge_error_message,
    get_result_value,
    map_result_error,
    localized_error,
)
from modules.assembly_scripts import build_create_joint_script, build_create_component_script

ASSEMBLY_ERROR_MAP = {
    "ERR_COMP": localized_error("component_not_found"),
    "ERR_COMPONENT": localized_error("component_not_found"),
}

def create_component_logic(name: str = "New Component", lang: str = "en"):
    """Creates a new empty component in the root design."""
    try:
        res = execute_fusion_script(build_create_component_script(), {"name": name})
        val = get_result_value(res)
        err = map_result_error(val, lang, ASSEMBLY_ERROR_MAP)
        if err: return err
        return f"Component '{val}' created."
    except FusionBridgeError as e: return bridge_error_message(e)

def create_joint_logic(comp1: str, comp2: str, joint_type: str = "Rigid", lang: str = "en"):
    """Creates a joint between two components."""
    try:
        res = execute_fusion_script(build_create_joint_script(), {"c1":comp1, "c2":comp2, "type":joint_type}, use_common=["find_comp"])
        val = get_result_value(res)
        err = map_result_error(val, lang, ASSEMBLY_ERROR_MAP)
        if err: return err
        return format_response(lang, "joint_created", type=joint_type)
    except FusionBridgeError as e: return bridge_error_message(e)

def register_assembly_tools(mcp):
    register_tool(mcp, "create_component", create_component_logic)
    register_tool(mcp, "create_joint", create_joint_logic)
