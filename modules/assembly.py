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
    "ERR_ROOT_COMPONENT": "Error: The root component cannot be edited by this action.",
    "ERR_NEW_NAME_REQUIRED": "Error: new_name is required for this assembly action.",
}


def _handle_assembly_batch_result(val: str, lang: str):
    parts = [part for part in str(val).split(",") if part]
    errors = [part for part in parts if ":ERR" in part or "ERR_" in part]
    if errors:
        mapped_errors = []
        for err_part in errors:
            mapped = None
            for code, message in ASSEMBLY_ERROR_MAP.items():
                if code in err_part:
                    if isinstance(message, dict) and message.get("type") == "i18n":
                        mapped = format_response(lang, message["key"], **message.get("kwargs", {}))
                    else:
                        mapped = message
                    break
            mapped_errors.append(mapped or err_part)
        return f"Error: Some assembly operations failed: {'; '.join(mapped_errors)}"
    return None

def edit_assembly_logic(operations: list[dict], lang: str = "en"):
    """
    Executes multiple assembly operations in a single batch.
    Supported actions: create_component, create_joint, create_as_built_joint,
    set_contact_sets, rename_component, delete_component, move_component.
    Component references should prefer component_path over plain names for nested assemblies.
    Each operation should be a dict with 'action' and required parameters.
    """
    try:
        res = execute_fusion_script(build_edit_assembly_script(), {"operations": operations}, use_common=["find_body"])
        val = get_result_value(res)
        err = _handle_assembly_batch_result(str(val), lang)
        if err:
            return err
        return format_response(lang, "assembly_updated")
    except FusionBridgeError as e: return bridge_error_message(e)

def register_assembly_tools(mcp):
    register_tool(mcp, "edit_assembly", edit_assembly_logic)
