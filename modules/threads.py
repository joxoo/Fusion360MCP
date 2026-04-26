from core.bridge import execute_fusion_script, FusionBridgeError
from core.utils import format_response, register_tool
from modules.threads_scripts import build_apply_custom_thread_script

def apply_custom_thread_logic(body_name: str, thread_type: str, size: str, designation: str, thread_class: str = "", is_modeled: bool = True, lang: str = "en"):
    """Business logic for applying specific thread data."""
    try:
        res = execute_fusion_script(build_apply_custom_thread_script(), {
            "body_name": body_name, "type": thread_type, "size": size,
            "designation": designation, "class": thread_class, "modeled": is_modeled
        }, use_common=["find_body"])
        val = res.get("data", ["ERR_UNKNOWN"])[0]
        if val == "ERR_BODY": return format_response(lang, "body_not_found")
        if val == "ERR_FACE": return format_response(lang, "face_not_found")
        if val == "ERR_TYPE": return format_response(lang, "thread_type_not_found")
        if val == "ERR_SIZE": return format_response(lang, "size_not_found")
        if val == "ERR_DESIG": return format_response(lang, "designation_not_found")
        if isinstance(val, str) and val.startswith("ERR_"): return format_response(lang, "unknown_error")
        return format_response(lang, "thread_applied", name=val)
    except FusionBridgeError as e: return f"Error: {str(e)}"

def register_thread_tools(mcp):
    register_tool(mcp, "apply_custom_thread", apply_custom_thread_logic)
