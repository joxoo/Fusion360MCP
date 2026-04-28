from core.bridge import execute_fusion_script, FusionBridgeError
from core.utils import format_response, register_tool
from core.error_handler import bridge_error_message, get_result_value, localized_error, map_result_error
from modules.forms_scripts import (
    build_create_form_box_script,
    build_create_form_sphere_script,
    build_create_form_cylinder_script,
    build_create_form_plane_script,
    build_create_form_torus_script,
    build_create_form_extrude_script,
    build_create_form_revolve_script,
    build_create_form_sweep_script,
    build_create_form_loft_script,
    build_insert_form_edge_script,
    build_subdivide_form_face_script,
    build_create_form_crease_script,
    build_create_form_mirror_internal_script,
    build_clear_form_symmetry_script,
    build_set_form_display_mode_script,
    build_bridge_form_entities_script,
    build_fill_form_hole_script,
    build_convert_form_script,
)

def set_form_display_mode_logic(body: str, mode: str = "Smooth", lang: str = "en"):
    """Sets the display mode of a T-Spline form (Box, Smooth)."""
    try:
        res = execute_fusion_script(build_set_form_display_mode_script(), {"body": body, "mode": mode}, use_common=["find_body"])
        val = get_result_value(res)
        mapped_error = map_result_error(val, lang, {"ERR_NOT_A_FORM": "Error: Target body is not a T-Spline form."})
        if mapped_error:
            return mapped_error
        return f"Display mode for '{body}' set to {mode}."
    except FusionBridgeError as e: return bridge_error_message(e)

def bridge_form_entities_logic(body: str, lang: str = "en"):
    """Bridges two sets of entities in a T-Spline form."""
    try:
        res = execute_fusion_script(build_bridge_form_entities_script(), {"body": body}, use_common=["find_body"])
        val = get_result_value(res)
        mapped_error = map_result_error(val, lang, {"ERR_NOT_A_FORM": "Error: Target body is not a T-Spline form."})
        if mapped_error:
            return mapped_error
        return f"Bridge created in '{body}'."
    except FusionBridgeError as e: return bridge_error_message(e)

def fill_form_hole_logic(body: str, lang: str = "en"):
    """Fills a hole in a T-Spline form."""
    try:
        res = execute_fusion_script(build_fill_form_hole_script(), {"body": body}, use_common=["find_body"])
        val = get_result_value(res)
        mapped_error = map_result_error(val, lang, {"ERR_NOT_A_FORM": "Error: Target body is not a T-Spline form."})
        if mapped_error:
            return mapped_error
        return f"Hole filled in '{body}'."
    except FusionBridgeError as e: return bridge_error_message(e)

def convert_form_logic(body: str, lang: str = "en"):
    """Converts a T-Spline form to a solid body."""
    try:
        res = execute_fusion_script(build_convert_form_script(), {"body": body}, use_common=["find_body"])
        val = get_result_value(res)
        mapped_error = map_result_error(val, lang, {"ERR_NOT_A_FORM": "Error: Target body is not a T-Spline form."})
        if mapped_error:
            return mapped_error
        return f"Form '{body}' successfully converted to solid."
    except FusionBridgeError as e: return bridge_error_message(e)

def create_form_mirror_internal_logic(body: str, lang: str = "en"):
    """Creates internal mirror symmetry in a T-Spline form."""
    try:
        res = execute_fusion_script(build_create_form_mirror_internal_script(), {"body": body}, use_common=["find_body"])
        val = get_result_value(res)
        mapped_error = map_result_error(val, lang, {"ERR_NOT_A_FORM": "Error: Target body is not a T-Spline form."})
        if mapped_error:
            return mapped_error
        return f"Internal mirror symmetry created in '{body}'."
    except FusionBridgeError as e: return bridge_error_message(e)

def clear_form_symmetry_logic(body: str, lang: str = "en"):
    """Clears all symmetry from a T-Spline form."""
    try:
        res = execute_fusion_script(build_clear_form_symmetry_script(), {"body": body}, use_common=["find_body"])
        val = get_result_value(res)
        mapped_error = map_result_error(val, lang, {"ERR_NOT_A_FORM": "Error: Target body is not a T-Spline form."})
        if mapped_error:
            return mapped_error
        return f"All symmetry cleared from '{body}'."
    except FusionBridgeError as e: return bridge_error_message(e)

def insert_form_edge_logic(body: str, lang: str = "en"):
    """Inserts a new edge into a T-Spline form."""
    try:
        res = execute_fusion_script(build_insert_form_edge_script(), {"body": body}, use_common=["find_body"])
        val = get_result_value(res)
        mapped_error = map_result_error(val, lang, {"ERR_NOT_A_FORM": "Error: Target body is not a T-Spline form."})
        if mapped_error:
            return mapped_error
        return f"Edge inserted into '{body}'."
    except FusionBridgeError as e: return bridge_error_message(e)

def subdivide_form_face_logic(body: str, lang: str = "en"):
    """Subdivides a face of a T-Spline form."""
    try:
        res = execute_fusion_script(build_subdivide_form_face_script(), {"body": body}, use_common=["find_body"])
        val = get_result_value(res)
        mapped_error = map_result_error(val, lang, {"ERR_NOT_A_FORM": "Error: Target body is not a T-Spline form."})
        if mapped_error:
            return mapped_error
        return f"Face subdivided in '{body}'."
    except FusionBridgeError as e: return bridge_error_message(e)

def create_form_crease_logic(body: str, lang: str = "en"):
    """Creates a sharp crease on T-Spline edges."""
    try:
        res = execute_fusion_script(build_create_form_crease_script(), {"body": body}, use_common=["find_body"])
        val = get_result_value(res)
        mapped_error = map_result_error(val, lang, {"ERR_NOT_A_FORM": "Error: Target body is not a T-Spline form."})
        if mapped_error:
            return mapped_error
        return f"Crease created on '{body}' edges."
    except FusionBridgeError as e: return bridge_error_message(e)

def create_form_extrude_logic(sketch: str, dist: float, symmetric: bool = False, lang: str = "en", component_name: str = None, component_path: str = None):
    """Extrudes a sketch profile into a T-Spline form."""
    try:
        res = execute_fusion_script(build_create_form_extrude_script(), {
            "sketch": sketch, "dist": dist, "symmetric": symmetric,
            "component_name": component_name, "component_path": component_path
        }, use_common=["find_body"])
        val = get_result_value(res)
        mapped_error = map_result_error(val, lang, {
            "ERR_SKETCH": localized_error("sketch_not_found"),
            "ERR_COMPONENT": localized_error("component_not_found"),
        })
        if mapped_error:
            return mapped_error
        return f"Form extrude created: {val}"
    except FusionBridgeError as e: return bridge_error_message(e)

def create_form_revolve_logic(sketch: str, axis: str = "Z", angle: float = 360.0, lang: str = "en", component_name: str = None, component_path: str = None):
    """Revolves a sketch profile into a T-Spline form."""
    try:
        res = execute_fusion_script(build_create_form_revolve_script(), {
            "sketch": sketch, "axis": axis, "angle": angle,
            "component_name": component_name, "component_path": component_path
        }, use_common=["find_body"])
        val = get_result_value(res)
        mapped_error = map_result_error(val, lang, {
            "ERR_SKETCH": localized_error("sketch_not_found"),
            "ERR_COMPONENT": localized_error("component_not_found"),
        })
        if mapped_error:
            return mapped_error
        return f"Form revolve created: {val}"
    except FusionBridgeError as e: return bridge_error_message(e)

def create_form_sweep_logic(profile_sketch: str, path_sketch: str, lang: str = "en", component_name: str = None, component_path: str = None):
    """Sweeps a sketch profile into a T-Spline form along a path."""
    try:
        res = execute_fusion_script(build_create_form_sweep_script(), {
            "profile_sketch": profile_sketch, "path_sketch": path_sketch,
            "component_name": component_name, "component_path": component_path
        }, use_common=["find_body"])
        val = get_result_value(res)
        mapped_error = map_result_error(val, lang, {
            "ERR_INPUT": "Error: Profile sketch or path sketch not found.",
            "ERR_COMPONENT": localized_error("component_not_found"),
            "ERR_OWNER_MISMATCH": localized_error("entity_owner_mismatch"),
        })
        if mapped_error:
            return mapped_error
        return f"Form sweep created: {val}"
    except FusionBridgeError as e: return bridge_error_message(e)

def create_form_loft_logic(sketch_names: list, lang: str = "en", component_name: str = None, component_path: str = None):
    """Lofts multiple sketch profiles into a T-Spline form."""
    try:
        res = execute_fusion_script(build_create_form_loft_script(), {
            "sketch_names": sketch_names,
            "component_name": component_name,
            "component_path": component_path
        }, use_common=["find_body"])
        val = get_result_value(res)
        mapped_error = map_result_error(val, lang, {
            "ERR_MIN_PROFILES": "Error: At least 2 profiles required for form loft.",
            "ERR_COMPONENT": localized_error("component_not_found"),
            "ERR_OWNER_MISMATCH": localized_error("entity_owner_mismatch"),
        })
        if mapped_error:
            return mapped_error
        return f"Form loft created: {val}"
    except FusionBridgeError as e: return bridge_error_message(e)

def create_form_box_logic(l: float, w: float, h: float, x: float = 0, y: float = 0, z: float = 0, l_faces: int = 2, w_faces: int = 2, h_faces: int = 2, lang: str = "en"):
    """Creates an organic T-Spline box."""
    try:
        res = execute_fusion_script(build_create_form_box_script(), {
            "l": l, "w": w, "h": h, "x": x, "y": y, "z": z, "l_faces": l_faces, "w_faces": w_faces, "h_faces": h_faces
        }, use_common=["find_body"])
        val = get_result_value(res)
        if val == "ERR_UNSUPPORTED":
            return "Error: T-Spline primitive creation is not exposed by the current Fusion API/runtime."
        if isinstance(val, str) and val.startswith("ERR_"): return val
        return f"Form box '{val}' created."
    except FusionBridgeError as e: return bridge_error_message(e)

def create_form_sphere_logic(dia: float, x: float = 0, y: float = 0, z: float = 0, long_faces: int = 8, lat_faces: int = 8, lang: str = "en"):
    """Creates an organic T-Spline sphere."""
    try:
        res = execute_fusion_script(build_create_form_sphere_script(), {
            "dia": dia, "x": x, "y": y, "z": z, "long_faces": long_faces, "lat_faces": lat_faces
        }, use_common=["find_body"])
        val = get_result_value(res)
        if val == "ERR_UNSUPPORTED":
            return "Error: T-Spline primitive creation is not exposed by the current Fusion API/runtime."
        if isinstance(val, str) and val.startswith("ERR_"): return val
        return f"Form sphere '{val}' created."
    except FusionBridgeError as e: return bridge_error_message(e)

def create_form_cylinder_logic(r: float, h: float, x: float = 0, y: float = 0, z: float = 0, h_faces: int = 4, d_faces: int = 8, lang: str = "en"):
    """Creates an organic T-Spline cylinder."""
    try:
        res = execute_fusion_script(build_create_form_cylinder_script(), {
            "r": r, "h": h, "x": x, "y": y, "z": z, "h_faces": h_faces, "d_faces": d_faces
        }, use_common=["find_body"])
        val = get_result_value(res)
        if val == "ERR_UNSUPPORTED":
            return "Error: T-Spline primitive creation is not exposed by the current Fusion API/runtime."
        if isinstance(val, str) and val.startswith("ERR_"): return val
        return f"Form cylinder '{val}' created."
    except FusionBridgeError as e: return bridge_error_message(e)

def create_form_plane_logic(l: float, w: float, x: float = 0, y: float = 0, z: float = 0, l_faces: int = 2, w_faces: int = 2, lang: str = "en"):
    """Creates an organic T-Spline plane."""
    try:
        res = execute_fusion_script(build_create_form_plane_script(), {
            "l": l, "w": w, "x": x, "y": y, "z": z, "l_faces": l_faces, "w_faces": w_faces
        }, use_common=["find_body"])
        val = get_result_value(res)
        if val == "ERR_UNSUPPORTED":
            return "Error: T-Spline primitive creation is not exposed by the current Fusion API/runtime."
        if isinstance(val, str) and val.startswith("ERR_"): return val
        return f"Form plane '{val}' created."
    except FusionBridgeError as e: return bridge_error_message(e)

def create_form_torus_logic(major_r: float, minor_r: float, x: float = 0, y: float = 0, z: float = 0, r_faces: int = 8, p_faces: int = 8, lang: str = "en"):
    """Creates an organic T-Spline torus."""
    try:
        res = execute_fusion_script(build_create_form_torus_script(), {
            "major_r": major_r, "minor_r": minor_r, "x": x, "y": y, "z": z, "r_faces": r_faces, "p_faces": p_faces
        }, use_common=["find_body"])
        val = get_result_value(res)
        if val == "ERR_UNSUPPORTED":
            return "Error: T-Spline primitive creation is not exposed by the current Fusion API/runtime."
        if isinstance(val, str) and val.startswith("ERR_"): return val
        return f"Form torus '{val}' created."
    except FusionBridgeError as e: return bridge_error_message(e)

def register_form_tools(mcp):
    register_tool(mcp, "create_form_extrude", create_form_extrude_logic)
    register_tool(mcp, "create_form_revolve", create_form_revolve_logic)
    register_tool(mcp, "create_form_sweep", create_form_sweep_logic)
    register_tool(mcp, "create_form_loft", create_form_loft_logic)
    register_tool(mcp, "create_form_mirror_internal", create_form_mirror_internal_logic)
    register_tool(mcp, "clear_form_symmetry", clear_form_symmetry_logic)
    register_tool(mcp, "insert_form_edge", insert_form_edge_logic)
    register_tool(mcp, "subdivide_form_face", subdivide_form_face_logic)
    register_tool(mcp, "create_form_crease", create_form_crease_logic)
    register_tool(mcp, "set_form_display_mode", set_form_display_mode_logic)
    register_tool(mcp, "bridge_form_entities", bridge_form_entities_logic)
    register_tool(mcp, "fill_form_hole", fill_form_hole_logic)
    register_tool(mcp, "convert_form", convert_form_logic)
    register_tool(mcp, "create_form_box", create_form_box_logic)
    register_tool(mcp, "create_form_sphere", create_form_sphere_logic)
    register_tool(mcp, "create_form_cylinder", create_form_cylinder_logic)
    register_tool(mcp, "create_form_plane", create_form_plane_logic)
    register_tool(mcp, "create_form_torus", create_form_torus_logic)
