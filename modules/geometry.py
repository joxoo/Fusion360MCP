from core.bridge import execute_fusion_script, FusionBridgeError
from core.utils import format_response, register_tool
from core.error_handler import (
    bridge_error_message,
    get_result_value,
    map_result_error,
    localized_error,
)
from modules.geometry_scripts import (
    build_create_chamfer_script,
    build_create_shell_script,
    build_mirror_body_script,
    build_create_box_script,
    build_create_circular_pattern_script,
    build_create_rectangular_pattern_script,
    build_create_fillet_script,
    build_create_edge_fillet_script,
    build_extrude_sketch_script,
    build_create_hole_script,
    build_create_cylinder_script,
    build_create_sphere_script,
    build_create_torus_script,
    build_create_coil_script,
    build_create_pipe_script,
    build_create_revolve_script,
    build_create_sweep_script,
    build_create_feature_pattern_script,
    build_create_boundary_fill_script,
    build_create_hole_advanced_script,
    build_create_pattern_on_path_script,
    build_mirror_features_script,
    build_combine_bodies_script,
    build_split_body_script,
    build_scale_body_script,
    build_move_body_script,
    build_move_body_absolute_script,
    build_delete_body_script,
    build_rename_body_script,
    build_get_feature_history_script,
    build_delete_feature_script,
    build_edit_feature_script,
    build_delete_face_script,
    build_offset_face_script,
    build_move_face_script,
    build_create_plastic_rib_script,
    build_create_plastic_web_script,
    build_create_plastic_boss_script,
    build_create_snap_fit_script,
)
import json

GEOMETRY_ERROR_MAP = {
    "ERR_NOT_FOUND": localized_error("body_not_found"),
    "ERR_BODY": localized_error("body_not_found"),
    "ERROR": localized_error("body_not_found"),
    "ERR_COMPONENT": localized_error("component_not_found"),
    "ERR_OWNER_MISMATCH": localized_error("entity_owner_mismatch"),
    "ERR_SKETCH": localized_error("sketch_not_found"),
}

def get_feature_history_logic(lang: str = "en"):
    """Returns the timeline history of construction features."""
    try:
        res = execute_fusion_script(build_get_feature_history_script())
        return get_result_value(res, "[]")
    except FusionBridgeError as e: return bridge_error_message(e)

def delete_feature_logic(feature_name: str, lang: str = "en"):
    """Deletes a specific feature from the timeline."""
    try:
        res = execute_fusion_script(build_delete_feature_script(), {"feature_name": feature_name})
        val = get_result_value(res)
        error_map = {
            "ERR_NOT_FOUND": f"Error: Feature '{feature_name}' not found.",
        }
        err = map_result_error(val, lang, error_map)
        if err: return err
        return f"Feature '{feature_name}' deleted."
    except FusionBridgeError as e: return bridge_error_message(e)

def edit_feature_logic(feature_name: str, new_name: str = None, suppress: bool = None, value: str = None, lang: str = "en"):
    """Edits a feature (Rename, Suppress, or update simple parameters)."""
    params = {"feature_name": feature_name}
    if new_name is not None: params["new_name"] = new_name
    if suppress is not None: params["suppress"] = suppress
    if value is not None: params["value"] = value
    
    try:
        res = execute_fusion_script(build_edit_feature_script(), params)
        val = get_result_value(res)
        error_map = {
            "ERR_NOT_FOUND": f"Error: Feature '{feature_name}' not found.",
        }
        err = map_result_error(val, lang, error_map)
        if err: return err
        return f"Feature '{feature_name}' updated."
    except FusionBridgeError as e: return bridge_error_message(e)

def delete_face_logic(body: str, face_index: int = 0, lang: str = "en"):
    """Deletes a specific face from a body (Direct Modeling)."""
    try:
        res = execute_fusion_script(build_delete_face_script(), {"body": body, "face_index": face_index}, use_common=["find_body"])
        val = get_result_value(res)
        error_map = {
            **GEOMETRY_ERROR_MAP,
            "ERR_FACE_INDEX": "Error: Invalid face index.",
        }
        err = map_result_error(val, lang, error_map)
        if err: return err
        return f"Face {face_index} of '{body}' deleted."
    except FusionBridgeError as e: return bridge_error_message(e)

def offset_face_logic(body: str, dist: float, face_index: int = 0, lang: str = "en"):
    """Offsets a specific face (Direct Modeling)."""
    try:
        res = execute_fusion_script(build_offset_face_script(), {"body": body, "dist": dist, "face_index": face_index}, use_common=["find_body"])
        val = get_result_value(res)
        err = map_result_error(val, lang, GEOMETRY_ERROR_MAP)
        if err: return err
        return f"Face {face_index} of '{body}' offset by {dist} cm."
    except FusionBridgeError as e: return bridge_error_message(e)

def move_face_logic(body: str, x: float, y: float, z: float, face_index: int = 0, lang: str = "en"):
    """Moves a specific face (Direct Modeling)."""
    try:
        res = execute_fusion_script(build_move_face_script(), {"body": body, "x": x, "y": y, "z": z, "face_index": face_index}, use_common=["find_body"])
        val = get_result_value(res)
        err = map_result_error(val, lang, GEOMETRY_ERROR_MAP)
        if err: return err
        return f"Face {face_index} of '{body}' moved."
    except FusionBridgeError as e: return bridge_error_message(e)

def create_plastic_rib_logic(path_sketch: str, thickness: float, lang: str = "en"):
    """Creates a plastic rib from a sketch path."""
    try:
        res = execute_fusion_script(build_create_plastic_rib_script(), {"path_sketch": path_sketch, "thick": thickness}, use_common=["find_body"])
        val = get_result_value(res)
        error_map = {
            "ERR_PATH": "Error: Sketch path not found.",
        }
        err = map_result_error(val, lang, error_map)
        if err: return err
        return f"Plastic rib '{val}' created."
    except FusionBridgeError as e: return bridge_error_message(e)

def create_plastic_web_logic(path_sketch: str, thickness: float, lang: str = "en"):
    """Creates a plastic web structure."""
    try:
        res = execute_fusion_script(build_create_plastic_web_script(), {"path_sketch": path_sketch, "thick": thickness}, use_common=["find_body"])
        val = get_result_value(res)
        error_map = {
            "ERR_PATH": "Error: Sketch path not found.",
        }
        err = map_result_error(val, lang, error_map)
        if err: return err
        return f"Plastic web '{val}' created."
    except FusionBridgeError as e: return bridge_error_message(e)

def create_plastic_boss_logic(path_sketch: str, is_threaded: bool = True, lang: str = "en"):
    """Creates automated mounting bosses."""
    try:
        res = execute_fusion_script(build_create_plastic_boss_script(), {"path_sketch": path_sketch, "is_thread": is_threaded}, use_common=["find_body"])
        val = get_result_value(res)
        error_map = {
            "ERR_POINTS": "Error: No sketch points found for boss placement.",
            "ERR_UNSUPPORTED": "Error: Plastic Boss is not exposed by the current Fusion API/runtime.",
            "ERR_EXTENSION": "Error: This feature requires the 'Product Design Extension' which is not available.",
            "ERR_SKETCH": localized_error("sketch_not_found"),
        }
        err = map_result_error(val, lang, error_map)
        if err: return err
        return f"Plastic boss '{val}' created."
    except FusionBridgeError as e: return bridge_error_message(e)

def create_snap_fit_logic(path_sketch: str, lang: str = "en"):
    """Creates a snap fit clip."""
    try:
        res = execute_fusion_script(build_create_snap_fit_script(), {"path_sketch": path_sketch}, use_common=["find_body"])
        val = get_result_value(res)
        error_map = {
            "ERR_POINT": "Error: No sketch point found for snap fit.",
            "ERR_UNSUPPORTED": "Error: Snap Fit is not exposed by the current Fusion API/runtime.",
        }
        err = map_result_error(val, lang, error_map)
        if err: return err
        return f"Snap fit '{val}' created."
    except FusionBridgeError as e: return bridge_error_message(e)

def combine_bodies_logic(
    target: str,
    tool_bodies: list,
    operation: str = "Join",
    lang: str = "en",
    component_name: str = None,
    component_path: str = None,
):
    """Combines multiple bodies into one (Join, Cut, Intersect)."""
    try:
        res = execute_fusion_script(build_combine_bodies_script(), {
            "target": target,
            "tool_bodies": tool_bodies,
            "operation": operation,
            "component_name": component_name,
            "component_path": component_path,
        }, use_common=["find_body"])
        val = get_result_value(res)
        error_map = {
            **GEOMETRY_ERROR_MAP,
            "ERR_COMBINE_FAILED_GEOMETRY": "Error: Fusion failed to combine these bodies. They might be touching but not overlapping enough. Use 'get_scene_map' to check positions and 'move_body_absolute' to ensure a 0.1mm overlap.",
        }
        err = map_result_error(val, lang, error_map)
        if err: return err
        return "Bodies successfully combined."
    except FusionBridgeError as e: return bridge_error_message(e)

def delete_body_logic(body: str, lang: str = "en"):
    """Permanently deletes a body from the design."""
    try:
        res = execute_fusion_script(build_delete_body_script(), {"body": body}, use_common=["find_body"])
        val = get_result_value(res)
        err = map_result_error(val, lang, GEOMETRY_ERROR_MAP)
        if err: return err
        return f"Body '{body}' deleted."
    except FusionBridgeError as e: return bridge_error_message(e)

def rename_body_logic(old_name: str, new_name: str, lang: str = "en"):
    """Renames a body to maintain organizational clarity."""
    try:
        res = execute_fusion_script(build_rename_body_script(), {"old_name": old_name, "new_name": new_name}, use_common=["find_body"])
        val = get_result_value(res)
        err = map_result_error(val, lang, GEOMETRY_ERROR_MAP)
        if err: return err
        return f"Body renamed from '{old_name}' to '{val}'."
    except FusionBridgeError as e: return bridge_error_message(e)

def split_body_logic(
    body: str,
    tool: str,
    lang: str = "en",
    component_name: str = None,
    component_path: str = None,
):
    """Splits a body using a plane or another body."""
    try:
        res = execute_fusion_script(build_split_body_script(), {
            "body": body,
            "tool": tool,
            "component_name": component_name,
            "component_path": component_path,
        }, use_common=["find_body"])
        val = get_result_value(res)
        error_map = {
            **GEOMETRY_ERROR_MAP,
            "ERR_BODY": localized_error("body_not_found"),
            "ERR_TOOL": f"Error: Splitting tool '{tool}' not found.",
        }
        err = map_result_error(val, lang, error_map)
        if err: return err
        return "Body successfully split."
    except FusionBridgeError as e: return bridge_error_message(e)

def scale_body_logic(body: str, factor: float, lang: str = "en"):
    """Scales a body by a given factor."""
    try:
        res = execute_fusion_script(build_scale_body_script(), {"body": body, "factor": factor}, use_common=["find_body"])
        val = get_result_value(res)
        err = map_result_error(val, lang, GEOMETRY_ERROR_MAP)
        if err: return err
        return f"Body '{body}' scaled by factor {factor}."
    except FusionBridgeError as e: return bridge_error_message(e)

def move_body_logic(body: str, x: float, y: float, z: float, angle: float = 0, lang: str = "en"):
    """Moves and/or rotates a body."""
    try:
        res = execute_fusion_script(build_move_body_script(), {
            "body": body, "x": x, "y": y, "z": z, "angle": angle
        }, use_common=["find_body"])
        val = get_result_value(res)
        err = map_result_error(val, lang, GEOMETRY_ERROR_MAP)
        if err: return err
        return f"Body '{body}' moved."
    except FusionBridgeError as e: return bridge_error_message(e)

def move_body_absolute_logic(body: str, x: float, y: float, z: float, lang: str = "en"):
    """Moves a body to an absolute center-of-mass position."""
    try:
        res = execute_fusion_script(build_move_body_absolute_script(), {
            "body": body, "x": x, "y": y, "z": z
        }, use_common=["find_body"])
        val = get_result_value(res)
        err = map_result_error(val, lang, GEOMETRY_ERROR_MAP)
        if err: return err
        if val == "OK": return f"Body '{body}' moved to absolute position ({x}, {y}, {z})."
        return val
    except FusionBridgeError as e: return bridge_error_message(e)

def create_pattern_on_path_logic(body: str, path_sketch: str, count: int, dist: float, symmetric: bool = False, lang: str = "en"):
    """Creates a pattern of a body along a sketch path."""
    try:
        res = execute_fusion_script(build_create_pattern_on_path_script(), {
            "body": body, "path_sketch": path_sketch, "count": count, "dist": dist, "symmetric": symmetric
        }, use_common=["find_body"])
        val = get_result_value(res)
        error_map = {
            "ERR_INPUT": "Error: Body or path sketch not found.",
        }
        err = map_result_error(val, lang, error_map)
        if err: return err
        return format_response(lang, "pattern_created")
    except FusionBridgeError as e: return bridge_error_message(e)

def mirror_features_logic(feature_name: str, plane_name: str, lang: str = "en"):
    """Mirrors a specific feature across a plane."""
    try:
        res = execute_fusion_script(build_mirror_features_script(), {"feature_name": feature_name, "plane": plane_name})
        val = get_result_value(res)
        error_map = {
            "ERR_FEATURE": f"Error: Feature '{feature_name}' not found.",
        }
        err = map_result_error(val, lang, error_map)
        if err: return err
        return format_response(lang, "mirror_created")
    except FusionBridgeError as e: return bridge_error_message(e)

def create_hole_advanced_logic(body: str, dia: float, depth: float, x: float = 0, y: float = 0, hole_type: str = "Simple", cb_dia: float = 0, cb_depth: float = 0, cs_dia: float = 0, cs_angle: float = 90.0, through_all: bool = False, is_threaded: bool = False, thread_desig: str = "", thread_type: str = "ISO Metric profile", lang: str = "en"):
    """Creates a professional hole (Counterbore, Countersink, Tapped)."""
    try:
        res = execute_fusion_script(build_create_hole_advanced_script(), {
            "body": body, "dia": dia, "depth": depth, "x": x, "y": y, 
            "hole_type": hole_type, "cb_dia": cb_dia, "cb_depth": cb_depth,
            "cs_dia": cs_dia, "cs_angle": cs_angle, "through_all": through_all,
            "is_threaded": is_threaded, "thread_desig": thread_desig, "thread_type": thread_type
        }, use_common=["find_body"])
        val = get_result_value(res)
        err = map_result_error(val, lang, GEOMETRY_ERROR_MAP)
        if err: return err
        return format_response(lang, "hole_created")
    except FusionBridgeError as e: return bridge_error_message(e)

def create_revolve_logic(sketch_name: str, axis: str = "Z", angle: float = 360.0, lang: str = "en"):
    """Revolves a sketch profile around an axis."""
    try:
        res = execute_fusion_script(build_create_revolve_script(), {"sketch": sketch_name, "axis": axis, "angle": angle}, use_common=["find_body"])
        val = get_result_value(res)
        err = map_result_error(val, lang, GEOMETRY_ERROR_MAP)
        if err: return err
        return f"Revolve feature created: {val}"
    except FusionBridgeError as e: return bridge_error_message(e)

def create_sweep_advanced_logic(
    profile_sketch: str,
    path_sketch: str,
    twist: float = 0,
    lang: str = "en",
    component_name: str = None,
    component_path: str = None,
):
    """Creates a sweep along a path with an optional twist angle."""
    try:
        res = execute_fusion_script(build_create_sweep_script(), {
            "profile_sketch": profile_sketch,
            "path_sketch": path_sketch,
            "twist": twist,
            "component_name": component_name,
            "component_path": component_path,
        }, use_common=["find_body"])
        val = get_result_value(res)
        error_map = {
            **GEOMETRY_ERROR_MAP,
            "ERR_INPUT": "Error: Profile sketch or path sketch not found.",
        }
        err = map_result_error(val, lang, error_map)
        if err: return err
        return f"Sweep feature '{val}' created."
    except FusionBridgeError as e: return bridge_error_message(e)

def create_feature_pattern_logic(feature_name: str, count: int, axis: str = "Z", lang: str = "en"):
    """Creates a circular pattern of a construction feature (e.g. an extrusion)."""
    try:
        res = execute_fusion_script(build_create_feature_pattern_script(), {
            "feature_name": feature_name, "count": count, "axis": axis
        })
        val = get_result_value(res)
        error_map = {
            "ERR_FEATURE_NOT_FOUND": f"Error: Feature '{feature_name}' not found.",
        }
        err = map_result_error(val, lang, error_map)
        if err: return err
        if val == "OK": return f"Feature pattern for '{feature_name}' created."
        return val
    except FusionBridgeError as e: return bridge_error_message(e)

def create_boundary_fill_logic(tool_bodies: list, lang: str = "en"):
    """Creates a solid from enclosed cells defined by tool bodies."""
    try:
        res = execute_fusion_script(build_create_boundary_fill_script(), {"tool_bodies": tool_bodies}, use_common=["find_body"])
        val = get_result_value(res)
        error_map = {
            "ERR_TOOLS": "Error: No valid tool bodies found.",
        }
        err = map_result_error(val, lang, error_map)
        if err: return err
        return f"Boundary fill created body: {val}"
    except FusionBridgeError as e: return bridge_error_message(e)

def create_cylinder_logic(r: float, h: float, name: str, x: float = 0, y: float = 0, z: float = 0, plane_name: str = "XY", lang: str = "en"):
    """Creates a massive cylinder."""
    try:
        res = execute_fusion_script(build_create_cylinder_script(), {"r": r, "h": h, "name": name, "x": x, "y": y, "z": z, "plane": plane_name})
        val = get_result_value(res)
        err = map_result_error(val, lang, GEOMETRY_ERROR_MAP)
        if err: return err
        return f"Cylinder '{val}' created."
    except FusionBridgeError as e: return bridge_error_message(e)

def create_sphere_logic(r: float, name: str, x: float = 0, y: float = 0, z: float = 0, lang: str = "en"):
    """Creates a sphere."""
    try:
        res = execute_fusion_script(build_create_sphere_script(), {"r": r, "name": name, "x": x, "y": y, "z": z})
        val = get_result_value(res)
        err = map_result_error(val, lang, GEOMETRY_ERROR_MAP)
        if err: return err
        return f"Sphere '{val}' created."
    except FusionBridgeError as e: return bridge_error_message(e)

def create_torus_logic(major_r: float, minor_r: float, name: str, x: float = 0, y: float = 0, z: float = 0, lang: str = "en"):
    """Creates a torus."""
    try:
        res = execute_fusion_script(build_create_torus_script(), {"major_r": major_r, "minor_r": minor_r, "name": name, "x": x, "y": y, "z": z})
        val = get_result_value(res)
        err = map_result_error(val, lang, GEOMETRY_ERROR_MAP)
        if err: return err
        return f"Torus '{val}' created."
    except FusionBridgeError as e: return bridge_error_message(e)

def create_coil_logic(dia: float, h: float, p: float, sec_t: float, name: str, x: float = 0, y: float = 0, z: float = 0, lang: str = "en"):
    """Creates a coil (spring)."""
    try:
        res = execute_fusion_script(build_create_coil_script(), {"dia": dia, "h": h, "p": p, "sec_t": sec_t, "name": name, "x": x, "y": y, "z": z})
        val = get_result_value(res)
        if "Command unavailable in this context" in val:
            return "Error: Coil creation is not available in the current Fusion command/runtime context."
        err = map_result_error(val, lang, GEOMETRY_ERROR_MAP)
        if err: return err
        return f"Coil '{val}' created."
    except FusionBridgeError as e: return bridge_error_message(e)

def create_pipe_logic(path_sketch: str, thickness: float, name: str, lang: str = "en"):
    """Creates a pipe along a sketch path."""
    try:
        res = execute_fusion_script(build_create_pipe_script(), {"path_sketch": path_sketch, "thickness": thickness, "name": name}, use_common=["find_body"])
        val = get_result_value(res)
        error_map = {
            "ERR_PATH": "Error: Sketch path not found.",
        }
        err = map_result_error(val, lang, error_map)
        if err: return err
        return f"Pipe '{val}' created."
    except FusionBridgeError as e: return bridge_error_message(e)

def create_chamfer_logic(body: str, distance: float, lang: str = "en"):
    """Adds a chamfer to all edges of a body."""
    try:
        res = execute_fusion_script(build_create_chamfer_script(), {"body":body, "dist":distance}, use_common=["find_body"])
        val = get_result_value(res)
        err = map_result_error(val, lang, GEOMETRY_ERROR_MAP)
        if err: return err
        return format_response(lang, "chamfer_created")
    except FusionBridgeError as e: return bridge_error_message(e)

def create_shell_logic(body: str, thickness: float, lang: str = "en"):
    """Hollows out a body with a given wall thickness."""
    try:
        res = execute_fusion_script(build_create_shell_script(), {"body":body, "thick":thickness}, use_common=["find_body"])
        val = get_result_value(res)
        err = map_result_error(val, lang, GEOMETRY_ERROR_MAP)
        if err: return err
        return format_response(lang, "shell_created")
    except FusionBridgeError as e: return bridge_error_message(e)

def mirror_body_logic(body: str, plane_name: str, lang: str = "en"):
    """Mirrors a body across a construction plane."""
    try:
        res = execute_fusion_script(build_mirror_body_script(), {"body":body, "plane":plane_name}, use_common=["find_body"])
        val = get_result_value(res)
        err = map_result_error(val, lang, GEOMETRY_ERROR_MAP)
        if err: return err
        return format_response(lang, "mirror_created")
    except FusionBridgeError as e: return bridge_error_message(e)

def create_box_logic(l: float, w: float, h: float, name: str, x: float = 0, y: float = 0, z: float = 0, op: str = "NewBody", taper: float = 0, lang: str = "en"):
    """Creates a basic box at specified coordinates."""
    try:
        res = execute_fusion_script(build_create_box_script(), {"l":l, "w":w, "h":h, "name":name, "x":x, "y":y, "z":z}, use_common=["placement"])
        val = get_result_value(res)
        error_map = {
            "ERR_NO_PROFILE": localized_error("sketch_not_found"),
        }
        err = map_result_error(val, lang, error_map)
        if err: return err
        return format_response(lang, "box_created", name=val)
    except FusionBridgeError as e: return bridge_error_message(e)

def create_circular_pattern_logic(body_name: str, count: int, axis: str = "Z", lang: str = "en"):
    """Creates a circular pattern of a body around an axis (X, Y, Z)."""
    try:
        res = execute_fusion_script(build_create_circular_pattern_script(), {"body": body_name, "count": count, "axis": axis}, use_common=["find_body"])
        val = get_result_value(res)
        err = map_result_error(val, lang, GEOMETRY_ERROR_MAP)
        if err: return err
        return format_response(lang, "pattern_created")
    except FusionBridgeError as e: return bridge_error_message(e)

def create_rectangular_pattern_logic(body_name: str, count_x: int, dist_x: float, count_y: int = 1, dist_y: float = 0, lang: str = "en"):
    """Creates a rectangular pattern of a body."""
    try:
        res = execute_fusion_script(build_create_rectangular_pattern_script(), {"body": body_name, "cx": count_x, "dx": dist_x, "cy": count_y, "dy": dist_y}, use_common=["find_body"])
        val = get_result_value(res)
        err = map_result_error(val, lang, GEOMETRY_ERROR_MAP)
        if err: return err
        return format_response(lang, "pattern_created")
    except FusionBridgeError as e: return bridge_error_message(e)

def create_fillet_logic(body_name: str, radius: float, lang: str = "en"):
    """Adds a fillet to all edges of a body."""
    try:
        res = execute_fusion_script(build_create_fillet_script(), {"body": body_name, "r": radius}, use_common=["find_body"])
        val = get_result_value(res)
        err = map_result_error(val, lang, GEOMETRY_ERROR_MAP)
        if err: return err
        return format_response(lang, "fillet_created")
    except FusionBridgeError as e: return bridge_error_message(e)

def create_edge_fillet_logic(body: str, radius: float, lang: str = "en"):
    """Creates fillets on specific edges of a body."""
    try:
        res = execute_fusion_script(build_create_edge_fillet_script(), {"body": body, "r": radius}, use_common=["find_body"])
        val = get_result_value(res)
        err = map_result_error(val, lang, GEOMETRY_ERROR_MAP)
        if err: return err
        return format_response(lang, "fillet_created")
    except FusionBridgeError as e: return bridge_error_message(e)

def extrude_sketch_logic(
    sketch_name: str,
    distance: float,
    lang: str = "en",
    profile_index: int = None,
    op: str = "NewBody",
    offset: float = 0,
    target_body: str = None,
    component_name: str = None,
    component_path: str = None,
):
    """Extrudes profiles of a sketch. Supports single profile selection, operations (Join, Cut, NewBody), start offset, and targeted body selection."""
    try:
        res = execute_fusion_script(build_extrude_sketch_script(), {
            "sketch": sketch_name,
            "dist": distance,
            "profile_index": profile_index,
            "op": op,
            "offset": offset,
            "target_body": target_body,
            "component_name": component_name,
            "component_path": component_path,
        }, use_common=["find_body"])
        val = get_result_value(res)
        error_map = {
            **GEOMETRY_ERROR_MAP,
            "ERR_NO_PROFILE": localized_error("sketch_not_found"),
            "ERR_TARGET_BODY": localized_error("body_not_found"),
        }
        err = map_result_error(val, lang, error_map)
        if err: return err
        return format_response(lang, "extrusion_created", name=sketch_name)
    except FusionBridgeError as e: return bridge_error_message(e)

def create_hole_logic(diameter_mm: float, x: float = 0, y: float = 0, lang: str = "en", z: float = 0):
    """Creates a simple hole in the active design."""
    try:
        res = execute_fusion_script(build_create_hole_script(), {"d": diameter_mm, "x": x, "y": y, "z": z}, use_common=["placement"])
        val = get_result_value(res)
        error_map = {
            "ERR_NO_PROFILE": localized_error("sketch_not_found"),
        }
        err = map_result_error(val, lang, error_map)
        if err: return err
        if val == "OK": return format_response(lang, "hole_created")
        return f"Error: {val}"
    except FusionBridgeError as e: return bridge_error_message(e)

def register_geometry_tools(mcp):
    register_tool(mcp, "create_box", create_box_logic)
    register_tool(mcp, "create_cylinder", create_cylinder_logic)
    register_tool(mcp, "create_sphere", create_sphere_logic)
    register_tool(mcp, "create_torus", create_torus_logic)
    register_tool(mcp, "create_coil", create_coil_logic)
    register_tool(mcp, "create_pipe", create_pipe_logic)
    register_tool(mcp, "create_revolve", create_revolve_logic)
    register_tool(mcp, "create_sweep_advanced", create_sweep_advanced_logic)
    register_tool(mcp, "create_feature_pattern", create_feature_pattern_logic)
    register_tool(mcp, "get_feature_history", get_feature_history_logic)
    register_tool(mcp, "delete_feature", delete_feature_logic)
    register_tool(mcp, "edit_feature", edit_feature_logic)
    register_tool(mcp, "create_boundary_fill", create_boundary_fill_logic)
    register_tool(mcp, "create_hole_advanced", create_hole_advanced_logic)
    register_tool(mcp, "create_hole", create_hole_logic)
    register_tool(mcp, "extrude_sketch", extrude_sketch_logic)
    register_tool(mcp, "create_circular_pattern", create_circular_pattern_logic)
    register_tool(mcp, "create_pattern_on_path", create_pattern_on_path_logic)
    register_tool(mcp, "mirror_features", mirror_features_logic)
    register_tool(mcp, "combine_bodies", combine_bodies_logic)
    register_tool(mcp, "delete_body", delete_body_logic)
    register_tool(mcp, "rename_body", rename_body_logic)
    register_tool(mcp, "split_body", split_body_logic)
    register_tool(mcp, "scale_body", scale_body_logic)
    register_tool(mcp, "move_body", move_body_logic)
    register_tool(mcp, "move_body_absolute", move_body_absolute_logic)
    register_tool(mcp, "create_plastic_rib", create_plastic_rib_logic)
    register_tool(mcp, "create_plastic_web", create_plastic_web_logic)
    register_tool(mcp, "create_plastic_boss", create_plastic_boss_logic)
    register_tool(mcp, "create_snap_fit", create_snap_fit_logic)
    register_tool(mcp, "delete_face", delete_face_logic)
    register_tool(mcp, "offset_face", offset_face_logic)
    register_tool(mcp, "move_face", move_face_logic)
    register_tool(mcp, "create_rectangular_pattern", create_rectangular_pattern_logic)
    register_tool(mcp, "create_chamfer", create_chamfer_logic)
    register_tool(mcp, "create_shell", create_shell_logic)
    register_tool(mcp, "create_fillet", create_fillet_logic)
    register_tool(mcp, "create_edge_fillet", create_edge_fillet_logic)
    register_tool(mcp, "mirror_body", mirror_body_logic)
