from core.utils import format_response


def bridge_error_message(error: Exception) -> str:
    return f"Error: {str(error)}"


def get_result_value(result: dict, default: str = ""):
    return result.get("data", [default])[0]


def localized_error(key: str, **kwargs) -> dict:
    return {"type": "i18n", "key": key, "kwargs": kwargs}


def map_result_error(val, lang: str, error_map: dict | None = None, passthrough_err_prefix: bool = True):
    if not isinstance(val, str):
        return None

    # Global taxonomy mapping
    global_map = {
        "ERR_COMPONENT_NOT_FOUND": localized_error("component_not_found"),
        "ERR_BODY_NOT_FOUND": localized_error("body_not_found"),
        "ERR_SKETCH_NOT_FOUND": localized_error("sketch_not_found"),
        "ERR_PROFILE_NOT_FOUND": localized_error("profile_not_found"),
        "ERR_FACE_NOT_FOUND": localized_error("face_not_found"),
        "ERR_ENTITY_OWNER_MISMATCH": localized_error("entity_owner_mismatch"),
        "ERR_CROSS_COMPONENT_NOT_SUPPORTED": localized_error("cross_component_operation_not_supported"),
    }

    full_map = {**global_map, **(error_map or {})}
    mapping = full_map.get(val)
    if mapping is None:
        if passthrough_err_prefix and val.startswith("ERR_"):
            return val
        return None

    if callable(mapping):
        mapping = mapping()

    if isinstance(mapping, dict) and mapping.get("type") == "i18n":
        return format_response(lang, mapping["key"], **mapping.get("kwargs", {}))

    return mapping
