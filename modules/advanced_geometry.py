from core.bridge import execute_fusion_script, FusionBridgeError
from core.utils import format_response, register_tool
from core.error_handler import bridge_error_message, get_result_value, localized_error, map_result_error
from modules.advanced_geometry_scripts import (
    build_create_loft_script,
    build_create_sweep_script,
    build_create_revolve_script,
    build_measure_distance_script,
    build_get_center_of_mass_script,
    build_apply_appearance_script,
)

def create_loft_logic(sketch_names: list, centerline_sketch: str = None, lang: str = "en", component_name: str = None, component_path: str = None):
    """Creates a loft feature between multiple sketches, optionally along a centerline."""
    try:
        res = execute_fusion_script(build_create_loft_script(), {
            "sketch_names": sketch_names,
            "centerline_sketch": centerline_sketch,
            "component_name": component_name,
            "component_path": component_path,
        }, use_common=["find_body"])
        val = get_result_value(res)
        mapped_error = map_result_error(val, lang, {
            "ERR_MIN_PROFILES": "Error: At least 2 valid sketches with profiles required.",
            "ERR_COMPONENT": localized_error("component_not_found"),
            "ERR_OWNER_MISMATCH": localized_error("entity_owner_mismatch"),
        })
        if mapped_error:
            return mapped_error
        return f"Loft created: {val}"
    except FusionBridgeError as e: return bridge_error_message(e)

def create_sweep_logic(
    profile_sketch: str,
    path_sketch: str,
    taper: float = 0,
    twist: float = 0,
    lang: str = "en",
    component_name: str = None,
    component_path: str = None,
):
    """Creates a sweep feature along a path with optional taper and twist."""
    try:
        res = execute_fusion_script(build_create_sweep_script(), {
            "profile_sketch": profile_sketch,
            "path_sketch": path_sketch,
            "taper": taper,
            "twist": twist,
            "component_name": component_name,
            "component_path": component_path,
        }, use_common=["find_body"])
        val = get_result_value(res)
        mapped_error = map_result_error(val, lang, {
            "ERR_INPUT_NOT_FOUND": "Error: Profile sketch or path sketch not found.",
            "ERR_COMPONENT": localized_error("component_not_found"),
            "ERR_OWNER_MISMATCH": localized_error("entity_owner_mismatch"),
        })
        if mapped_error:
            return mapped_error
        return f"Sweep created: {val}"
    except FusionBridgeError as e: return bridge_error_message(e)

def create_revolve_logic(
    profile_sketch: str,
    axis: str = "z",
    axis_sketch: str = None,
    angle: float = 6.283185,
    lang: str = "en",
    component_name: str = None,
    component_path: str = None,
):
    """Creates a revolve feature from a profile around an axis."""
    try:
        res = execute_fusion_script(build_create_revolve_script(), {
            "profile_sketch": profile_sketch,
            "axis": axis,
            "axis_sketch": axis_sketch,
            "angle": angle,
            "component_name": component_name,
            "component_path": component_path,
        }, use_common=["find_body"])
        val = get_result_value(res)
        mapped_error = map_result_error(val, lang, {
            "ERR_INPUT_NOT_FOUND": localized_error("sketch_not_found"),
            "ERR_COMPONENT": localized_error("component_not_found"),
        })
        if mapped_error: return mapped_error
        return f"Revolve created: {val}"
    except FusionBridgeError as e: return bridge_error_message(e)

def measure_distance_logic(body1: str, body2: str, lang: str = "en"):
    """Measures the minimum distance between two bodies."""
    try:
        res = execute_fusion_script(build_measure_distance_script(), {"body1": body1, "body2": body2}, use_common=["find_body"])
        val = get_result_value(res)
        mapped_error = map_result_error(val, lang, {"ERR_BODY": "Error: One or both bodies not found."})
        if mapped_error:
            return mapped_error
        return f"Distance: {val} cm"
    except FusionBridgeError as e: return bridge_error_message(e)

def get_center_of_mass_logic(body: str, lang: str = "en"):
    """Returns the center of mass coordinates for a body."""
    try:
        res = execute_fusion_script(build_get_center_of_mass_script(), {"body": body}, use_common=["find_body"])
        val = get_result_value(res)
        mapped_error = map_result_error(val, lang, {"ERR_BODY": "Error: Body not found."})
        if mapped_error:
            return mapped_error
        return f"Center of Mass (X,Y,Z): {val}"
    except FusionBridgeError as e: return bridge_error_message(e)

def apply_appearance_logic(body: str, appearance: str, lang: str = "en"):
    """Applies a visual appearance (color/texture) to a body."""
    try:
        res = execute_fusion_script(build_apply_appearance_script(), {"body": body, "appearance": appearance}, use_common=["find_body"])
        val = get_result_value(res)
        mapped_error = map_result_error(val, lang, {"ERR_NOT_FOUND": f"Error: Body or appearance '{appearance}' not found."})
        if mapped_error:
            return mapped_error
        return f"Appearance '{appearance}' applied to {body}."
    except FusionBridgeError as e: return bridge_error_message(e)

def register_advanced_geometry_tools(mcp):
    register_tool(mcp, "create_loft", create_loft_logic)
    register_tool(mcp, "create_sweep", create_sweep_logic)
    register_tool(mcp, "create_revolve", create_revolve_logic)
    register_tool(mcp, "measure_distance", measure_distance_logic)
    register_tool(mcp, "get_center_of_mass", get_center_of_mass_logic)
    register_tool(mcp, "apply_appearance", apply_appearance_logic)
