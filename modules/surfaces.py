from core.bridge import execute_fusion_script, FusionBridgeError
from core.utils import format_response, register_tool
from modules.surfaces_scripts import (
    build_create_surface_patch_script,
    build_offset_surface_script,
    build_stitch_surfaces_script,
    build_thicken_surface_script,
    build_create_surface_cylinder_script,
    build_create_surface_sphere_script,
    build_create_surface_torus_script,
    build_trim_surface_script,
    build_extend_surface_script,
    build_reverse_surface_normal_script,
)

def trim_surface_logic(body: str, tool_sketch: str, lang: str = "en"):
    """Trims a surface body using a sketch curve."""
    try:
        res = execute_fusion_script(build_trim_surface_script(), {"body": body, "tool_sketch": tool_sketch}, use_common=["find_body"])
        val = res.get("data", [""])[0]
        if val == "ERR_INPUT": return "Error: Body or tool sketch not found."
        if isinstance(val, str) and val.startswith("ERR_"): return val
        return f"Surface '{body}' trimmed successfully."
    except FusionBridgeError as e: return f"Error: {str(e)}"

def extend_surface_logic(body: str, distance: float, lang: str = "en"):
    """Extends a surface edge by a distance."""
    try:
        res = execute_fusion_script(build_extend_surface_script(), {"body": body, "dist": distance}, use_common=["find_body"])
        val = res.get("data", [""])[0]
        if val == "ERR_BODY": return format_response(lang, "body_not_found")
        if isinstance(val, str) and val.startswith("ERR_"): return val
        return f"Surface '{body}' extended by {distance} cm."
    except FusionBridgeError as e: return f"Error: {str(e)}"

def reverse_surface_normal_logic(body: str, lang: str = "en"):
    """Reverses the normal direction of a surface body."""
    try:
        res = execute_fusion_script(build_reverse_surface_normal_script(), {"body": body}, use_common=["find_body"])
        val = res.get("data", [""])[0]
        if val == "ERR_BODY": return format_response(lang, "body_not_found")
        if isinstance(val, str) and val.startswith("ERR_"): return val
        return f"Normal direction of '{body}' reversed."
    except FusionBridgeError as e: return f"Error: {str(e)}"

def create_surface_cylinder_logic(r: float, h: float, name: str, x: float = 0, y: float = 0, z: float = 0, plane_name: str = "XY", lang: str = "en"):
    """Creates a surface cylinder."""
    try:
        res = execute_fusion_script(build_create_surface_cylinder_script(), {"r": r, "h": h, "name": name, "x": x, "y": y, "z": z, "plane": plane_name})
        val = res.get("data", [""])[0]
        if isinstance(val, str) and val.startswith("ERR_"): return val
        return f"Surface cylinder '{val}' created."
    except FusionBridgeError as e: return f"Error: {str(e)}"

def create_surface_sphere_logic(r: float, name: str, x: float = 0, y: float = 0, z: float = 0, lang: str = "en"):
    """Creates a surface sphere."""
    try:
        res = execute_fusion_script(build_create_surface_sphere_script(), {"r": r, "name": name, "x": x, "y": y, "z": z})
        val = res.get("data", [""])[0]
        if isinstance(val, str) and val.startswith("ERR_"): return val
        return f"Surface sphere '{val}' created."
    except FusionBridgeError as e: return f"Error: {str(e)}"

def create_surface_torus_logic(major_r: float, minor_r: float, name: str, x: float = 0, y: float = 0, z: float = 0, lang: str = "en"):
    """Creates a surface torus."""
    try:
        res = execute_fusion_script(build_create_surface_torus_script(), {"major_r": major_r, "minor_r": minor_r, "name": name, "x": x, "y": y, "z": z})
        val = res.get("data", [""])[0]
        if isinstance(val, str) and val.startswith("ERR_"): return val
        return f"Surface torus '{val}' created."
    except FusionBridgeError as e: return f"Error: {str(e)}"

def create_surface_patch_logic(sketch_name: str, lang: str = "en"):
    """Creates a surface patch from a sketch profile."""
    try:
        res = execute_fusion_script(build_create_surface_patch_script(), {"sketch": sketch_name})
        val = res.get("data", [""])[0]
        if val == "ERR_SKETCH": return format_response(lang, "sketch_not_found")
        if isinstance(val, str) and val.startswith("ERR_"): return val
        return f"Surface patch created: {val}"
    except FusionBridgeError as e: return f"Error: {str(e)}"

def offset_surface_logic(body: str, distance: float, lang: str = "en"):
    """Creates an offset surface from an existing body's faces."""
    try:
        res = execute_fusion_script(build_offset_surface_script(), {"body": body, "dist": distance}, use_common=["find_body"])
        val = res.get("data", [""])[0]
        if val == "ERR_BODY": return format_response(lang, "body_not_found")
        if isinstance(val, str) and val.startswith("ERR_"): return val
        return f"Offset surface created: {val}"
    except FusionBridgeError as e: return f"Error: {str(e)}"

def stitch_surfaces_logic(body_names: list, tolerance: float = 0.1, lang: str = "en"):
    """Stitches multiple surfaces into a single body/solid."""
    try:
        res = execute_fusion_script(build_stitch_surfaces_script(), {"body_names": body_names, "tol": tolerance}, use_common=["find_body"])
        val = res.get("data", [""])[0]
        if val == "ERR_MIN_SURFACES": return "Error: At least one surface is required."
        if isinstance(val, str) and val.startswith("ERR_"): return val
        return f"Surfaces stitched successfully into: {val}"
    except FusionBridgeError as e: return f"Error: {str(e)}"

def thicken_surface_logic(body: str, thickness: float, lang: str = "en"):
    """Thickens a surface into a solid body."""
    try:
        res = execute_fusion_script(build_thicken_surface_script(), {"body": body, "thick": thickness}, use_common=["find_body"])
        val = res.get("data", [""])[0]
        if val == "ERR_BODY": return format_response(lang, "body_not_found")
        if isinstance(val, str) and val.startswith("ERR_"): return val
        return f"Surface thickened into solid: {val}"
    except FusionBridgeError as e: return f"Error: {str(e)}"

def register_surface_tools(mcp):
    register_tool(mcp, "create_surface_patch", create_surface_patch_logic)
    register_tool(mcp, "create_surface_cylinder", create_surface_cylinder_logic)
    register_tool(mcp, "create_surface_sphere", create_surface_sphere_logic)
    register_tool(mcp, "create_surface_torus", create_surface_torus_logic)
    register_tool(mcp, "trim_surface", trim_surface_logic)
    register_tool(mcp, "extend_surface", extend_surface_logic)
    register_tool(mcp, "reverse_surface_normal", reverse_surface_normal_logic)
    register_tool(mcp, "offset_surface", offset_surface_logic)
    register_tool(mcp, "stitch_surfaces", stitch_surfaces_logic)
    register_tool(mcp, "thicken_surface", thicken_surface_logic)
