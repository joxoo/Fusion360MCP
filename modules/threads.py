from core.bridge import execute_fusion_script, FusionBridgeError
from core.utils import format_response, register_tool
from core.error_handler import (
    bridge_error_message,
    get_result_value,
    map_result_error,
    localized_error,
)
from modules.threads_scripts import build_apply_custom_thread_script

THREADS_ERROR_MAP = {
    "ERR_BODY": localized_error("body_not_found"),
    "ERR_FACE": localized_error("face_not_found"),
    "ERR_TYPE": localized_error("thread_type_not_found"),
    "ERR_SIZE": localized_error("size_not_found"),
    "ERR_DESIG": localized_error("designation_not_found"),
    "ERR_UNKNOWN": localized_error("unknown_error"),
}

def apply_custom_thread_logic(body_name: str, thread_type: str, size: str, designation: str, thread_class: str = "", is_modeled: bool = True, lang: str = "en"):
    """Business logic for applying specific thread data."""
    try:
        res = execute_fusion_script(build_apply_custom_thread_script(), {
            "body_name": body_name, "type": thread_type, "size": size,
            "designation": designation, "class": thread_class, "modeled": is_modeled
        }, use_common=["find_body"])
        val = get_result_value(res, "ERR_UNKNOWN")
        err = map_result_error(val, lang, THREADS_ERROR_MAP)
        if err: return err
        return format_response(lang, "thread_applied", name=val)
    except FusionBridgeError as e: return bridge_error_message(e)

def register_thread_tools(mcp):
    register_tool(mcp, "apply_custom_thread", apply_custom_thread_logic)
