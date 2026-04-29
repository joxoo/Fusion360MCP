from core.bridge import execute_fusion_script, FusionBridgeError
from core.utils import format_response, register_tool
from core.error_handler import (
    bridge_error_message,
    get_result_value,
    map_result_error,
    localized_error,
)
from modules.assembly_scripts import (
    build_edit_assembly_script,
)

ASSEMBLY_ERROR_MAP = {
    "ERR_COMP": localized_error("component_not_found"),
    "ERR_COMPONENT": localized_error("component_not_found"),
}

def edit_assembly_logic(operations: list[dict], lang: str = "en"):
    """
    Executes multiple assembly operations in a single batch.
    Supported actions: create_component, create_joint.
    Each operation should be a dict with 'action' and required parameters.
    """
    try:
        res = execute_fusion_script(build_edit_assembly_script(), {"operations": operations}, use_common=["find_comp"])
        val = get_result_value(res)
        err = map_result_error(val, lang, ASSEMBLY_ERROR_MAP)
        if err: return err
        return format_response(lang, "assembly_updated")
    except FusionBridgeError as e: return bridge_error_message(e)

def register_assembly_tools(mcp):
    register_tool(mcp, "edit_assembly", edit_assembly_logic)
