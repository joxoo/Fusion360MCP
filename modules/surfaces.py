from core.bridge import execute_fusion_script, FusionBridgeError
from core.utils import format_response, register_tool
from core.error_handler import bridge_error_message, get_result_value, localized_error, map_result_error
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

def trim_surface_logic(body: str, tool_sketch: str, lang: str = "en", component_name: str = None, component_path: str = None):
    """Trims a surface body using a sketch curve."""
    try:
        res = execute_fusion_script(build_trim_surface_script(), {
            "body": body, "tool_sketch": tool_sketch,
            "component_name": component_name, "component_path": component_path
        }, use_common=["find_body"])
        val = get_result_value(res)
        mapped_error = map_result_error(val, lang, {
            "ERR_INPUT": "Error: Body or tool sketch not found.",
            "ERR_COMPONENT": localized_error("component_not_found"),
            "ERR_OWNER_MISMATCH": localized_error("entity_owner_mismatch"),
        })
        if mapped_error:
            return mapped_error
        return f"Surface '{body}' trimmed successfully."
    except FusionBridgeError as e: return bridge_error_message(e)

def extend_surface_logic(body: str, distance: float, lang: str = "en"):
    """Extends a surface edge by a distance."""
    try:
        res = execute_fusion_script(build_extend_surface_script(), {"body": body, "dist": distance}, use_common=["find_body"])
        val = get_result_value(res)
        mapped_error = map_result_error(val, lang, {"ERR_BODY": localized_error("body_not_found")})
        if mapped_error:
            return mapped_error
        return f"Surface '{body}' extended by {distance} cm."
    except FusionBridgeError as e: return bridge_error_message(e)

def reverse_surface_normal_logic(body: str, lang: str = "en"):
    """Reverses the normal direction of a surface body."""
    try:
        res = execute_fusion_script(build_reverse_surface_normal_script(), {"body": body}, use_common=["find_body"])
        val = get_result_value(res)
        mapped_error = map_result_error(val, lang, {"ERR_BODY": localized_error("body_not_found")})
        if mapped_error:
            return mapped_error
        return f"Normal direction of '{body}' reversed."
    except FusionBridgeError as e: return bridge_error_message(e)

def create_surface_cylinder_logic(r: float, h: float, name: str, x: float = 0, y: float = 0, z: float = 0, plane_name: str = "XY", lang: str = "en", component_name: str = None, component_path: str = None):
    """Creates a surface cylinder."""
    try:
        res = execute_fusion_script(build_create_surface_cylinder_script(), {
            "r": r, "h": h, "name": name, "x": x, "y": y, "z": z, "plane": plane_name,
            "component_name": component_name, "component_path": component_path
        }, use_common=["find_body"])
        val = get_result_value(res)
        mapped_error = map_result_error(val, lang, {"ERR_COMPONENT": localized_error("component_not_found")})
        if mapped_error:
            return mapped_error
        return f"Surface cylinder '{val}' created."
    except FusionBridgeError as e: return bridge_error_message(e)

def create_surface_sphere_logic(r: float, name: str, x: float = 0, y: float = 0, z: float = 0, lang: str = "en", component_name: str = None, component_path: str = None):
    """Creates a surface sphere."""
    try:
        res = execute_fusion_script(build_create_surface_sphere_script(), {
            "r": r, "name": name, "x": x, "y": y, "z": z,
            "component_name": component_name, "component_path": component_path
        }, use_common=["find_body"])
        val = get_result_value(res)
        mapped_error = map_result_error(val, lang, {"ERR_COMPONENT": localized_error("component_not_found")})
        if mapped_error:
            return mapped_error
        return f"Surface sphere '{val}' created."
    except FusionBridgeError as e: return bridge_error_message(e)

def create_surface_torus_logic(major_r: float, minor_r: float, name: str, x: float = 0, y: float = 0, z: float = 0, lang: str = "en", component_name: str = None, component_path: str = None):
    """Creates a surface torus."""
    try:
        res = execute_fusion_script(build_create_surface_torus_script(), {
            "major_r": major_r, "minor_r": minor_r, "name": name, "x": x, "y": y, "z": z,
            "component_name": component_name, "component_path": component_path
        }, use_common=["find_body"])
        val = get_result_value(res)
        mapped_error = map_result_error(val, lang, {"ERR_COMPONENT": localized_error("component_not_found")})
        if mapped_error:
            return mapped_error
        return f"Surface torus '{val}' created."
    except FusionBridgeError as e: return bridge_error_message(e)

def create_surface_patch_logic(sketch_name: str, lang: str = "en", component_name: str = None, component_path: str = None):
    """Creates a surface patch from a sketch profile."""
    try:
        res = execute_fusion_script(build_create_surface_patch_script(), {
            "sketch": sketch_name,
            "component_name": component_name, "component_path": component_path
        }, use_common=["find_body"])
        val = get_result_value(res)
        mapped_error = map_result_error(val, lang, {
            "ERR_SKETCH": localized_error("sketch_not_found"),
            "ERR_COMPONENT": localized_error("component_not_found"),
        })
        if mapped_error:
            return mapped_error
        return f"Surface patch created: {val}"
    except FusionBridgeError as e: return bridge_error_message(e)

def offset_surface_logic(body: str, distance: float, lang: str = "en"):
    """Creates an offset surface from an existing body's faces."""
    try:
        res = execute_fusion_script(build_offset_surface_script(), {"body": body, "dist": distance}, use_common=["find_body"])
        val = get_result_value(res)
        mapped_error = map_result_error(val, lang, {"ERR_BODY": localized_error("body_not_found")})
        if mapped_error:
            return mapped_error
        return f"Offset surface created: {val}"
    except FusionBridgeError as e: return bridge_error_message(e)

def stitch_surfaces_logic(body_names: list, tolerance: float = 0.1, lang: str = "en", component_name: str = None, component_path: str = None):
    """Stitches multiple surfaces into a single body/solid."""
    try:
        res = execute_fusion_script(build_stitch_surfaces_script(), {
            "body_names": body_names, "tol": tolerance,
            "component_name": component_name, "component_path": component_path
        }, use_common=["find_body"])
        val = get_result_value(res)
        mapped_error = map_result_error(val, lang, {
            "ERR_MIN_SURFACES": "Error: At least one surface is required.",
            "ERR_COMPONENT": localized_error("component_not_found"),
            "ERR_OWNER_MISMATCH": localized_error("entity_owner_mismatch"),
        })
        if mapped_error:
            return mapped_error
        return f"Surfaces stitched successfully into: {val}"
    except FusionBridgeError as e: return bridge_error_message(e)

def thicken_surface_logic(body: str, thickness: float, lang: str = "en"):
    """Thickens a surface into a solid body."""
    try:
        res = execute_fusion_script(build_thicken_surface_script(), {"body": body, "thick": thickness}, use_common=["find_body"])
        val = get_result_value(res)
        mapped_error = map_result_error(val, lang, {"ERR_BODY": localized_error("body_not_found")})
        if mapped_error:
            return mapped_error
        return f"Surface thickened into solid: {val}"
    except FusionBridgeError as e: return bridge_error_message(e)

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
