from core.bridge import execute_fusion_script, FusionBridgeError
from core.utils import format_response, register_tool
from modules.advanced_geometry_scripts import (
    build_create_loft_script,
    build_create_sweep_script,
    build_measure_distance_script,
    build_get_center_of_mass_script,
    build_apply_appearance_script,
    build_export_step_script,
)

def create_loft_logic(sketch_names: list, lang: str = "en"):
    """Creates a loft feature between multiple sketches."""
    try:
        res = execute_fusion_script(build_create_loft_script(), {"sketch_names": sketch_names})
        val = res.get("data", [""])[0]
        if val == "ERR_MIN_PROFILES": return "Error: At least 2 valid sketches with profiles required."
        if isinstance(val, str) and val.startswith("ERR_"): return val
        return f"Loft created: {val}"
    except FusionBridgeError as e: return f"Error: {str(e)}"

def create_sweep_logic(profile_sketch: str, path_sketch: str, lang: str = "en"):
    """Creates a sweep feature along a path."""
    try:
        res = execute_fusion_script(build_create_sweep_script(), {"profile_sketch": profile_sketch, "path_sketch": path_sketch})
        val = res.get("data", [""])[0]
        if val == "ERR_INPUT_NOT_FOUND": return "Error: Profile sketch or path sketch not found."
        if isinstance(val, str) and val.startswith("ERR_"): return val
        return f"Sweep created: {val}"
    except FusionBridgeError as e: return f"Error: {str(e)}"

def measure_distance_logic(body1: str, body2: str, lang: str = "en"):
    """Measures the minimum distance between two bodies."""
    try:
        res = execute_fusion_script(build_measure_distance_script(), {"body1": body1, "body2": body2}, use_common=["find_body"])
        val = res.get("data", [""])[0]
        if val == "ERR_BODY": return "Error: One or both bodies not found."
        return f"Distance: {val} cm"
    except FusionBridgeError as e: return f"Error: {str(e)}"

def get_center_of_mass_logic(body: str, lang: str = "en"):
    """Returns the center of mass coordinates for a body."""
    try:
        res = execute_fusion_script(build_get_center_of_mass_script(), {"body": body}, use_common=["find_body"])
        val = res.get("data", [""])[0]
        if val == "ERR_BODY": return "Error: Body not found."
        return f"Center of Mass (X,Y,Z): {val}"
    except FusionBridgeError as e: return f"Error: {str(e)}"

def apply_appearance_logic(body: str, appearance: str, lang: str = "en"):
    """Applies a visual appearance (color/texture) to a body."""
    try:
        res = execute_fusion_script(build_apply_appearance_script(), {"body": body, "appearance": appearance}, use_common=["find_body"])
        val = res.get("data", [""])[0]
        if val == "ERR_NOT_FOUND": return f"Error: Body or appearance '{appearance}' not found."
        return f"Appearance '{appearance}' applied to {body}."
    except FusionBridgeError as e: return f"Error: {str(e)}"

def export_step_logic(filename: str = "model", lang: str = "en"):
    """Exports the current design as a STEP file."""
    try:
        res = execute_fusion_script(build_export_step_script(), {"filename": filename})
        return res.get("data", ["Error"])[0]
    except FusionBridgeError as e: return f"Error: {str(e)}"

def register_advanced_geometry_tools(mcp):
    register_tool(mcp, "create_loft", create_loft_logic)
    register_tool(mcp, "create_sweep", create_sweep_logic)
    register_tool(mcp, "measure_distance", measure_distance_logic)
    register_tool(mcp, "get_center_of_mass", get_center_of_mass_logic)
    register_tool(mcp, "apply_appearance", apply_appearance_logic)
    register_tool(mcp, "export_step", export_step_logic)
