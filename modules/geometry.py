from core.bridge import execute_fusion_script, FusionBridgeError
from core.utils import format_response, register_tool
from core.error_handler import (
    bridge_error_message,
    get_result_value,
    map_result_error,
    localized_error,
)
from modules.geometry_scripts import (
    build_create_box_script,
    build_create_hole_script,
    build_create_cylinder_script,
    build_create_sphere_script,
    build_create_torus_script,
    build_create_coil_script,
    build_create_pipe_script,
    build_create_revolve_script,
    build_create_sweep_advanced_script,
    build_create_feature_pattern_script,
    build_get_feature_history_script,
    build_delete_feature_script,
    build_edit_feature_script,
    build_create_boundary_fill_script,
    build_create_hole_advanced_script,
    build_extrude_sketch_script,
    build_create_circular_pattern_script,
    build_create_pattern_on_path_script,
    build_mirror_features_script,
    build_combine_bodies_script,
    build_delete_body_script,
    build_rename_body_script,
    build_split_body_script,
    build_scale_body_script,
    build_move_body_script,
    build_move_body_absolute_script,
    build_create_plastic_rib_script,
    build_create_plastic_web_script,
    build_create_plastic_boss_script,
    build_create_snap_fit_script,
    build_delete_face_script,
    build_offset_face_script,
    build_move_face_script,
    build_create_rectangular_pattern_script,
    build_create_chamfer_script,
    build_create_shell_script,
    build_create_fillet_script,
    build_create_edge_fillet_script,
    build_mirror_body_script,
    build_apply_3d_features_script,
)
import json

GEOMETRY_ERROR_MAP = {
    "ERR_SKETCH": localized_error("sketch_not_found"),
    "ERR_BODY": localized_error("body_not_found"),
    "ERR_BODY_NOT_FOUND": localized_error("body_not_found"),
    "ERR_TARGET": localized_error("body_not_found"),
    "ERR_NOT_FOUND": localized_error("feature_not_found"),
    "ERR_FEATURE_NOT_FOUND": localized_error("feature_not_found"),
    "ERR_FEATURE_VALUE_UNSUPPORTED": "Error: This feature does not expose an editable value in the compact API.",
    "ERR_NEW_NAME_REQUIRED": "Error: new_name is required for this geometry action.",
    "ERR_DELETE_FAILED": "Error: Fusion reported that the body delete operation failed.",
    "ERR_VERIFICATION_FAILED": "Error: Geometry verification failed. The body was not created or is not visible.",
    "ERR_MIN_SURFACES": "Error: At least one surface is required.",
    "ERR_NO_PROFILE": "Error: No profile found in sketch.",
    "ERR_COMPONENT": localized_error("component_not_found"),
    "ERR_FACE_INDEX": "Error: face_index is out of range for the selected body.",
    "ERR_TOOL": "Error: A valid split tool or construction plane is required.",
    "ERR_OWNER_MISMATCH": localized_error("entity_owner_mismatch"),
}

def create_box_logic(l: float, w: float, h: float, name: str, x: float = 0, y: float = 0, z: float = 0, op: str = "NewBody", taper: float = 0, lang: str = "en"):
    """Creates a basic box at specified coordinates."""
    try:
        res = execute_fusion_script(build_create_box_script(), {"l":l, "w":w, "h":h, "name":name, "x":x, "y":y, "z":z}, use_common=["placement"])
        val = get_result_value(res)
        error_map = {"ERR_NO_PROFILE": localized_error("sketch_not_found"), "ERR_VERIFICATION_FAILED": GEOMETRY_ERROR_MAP["ERR_VERIFICATION_FAILED"]}
        err = map_result_error(val, lang, error_map)
        if err: return err
        return format_response(lang, "box_created", name=val)
    except FusionBridgeError as e: return bridge_error_message(e)

def delete_face_logic(body: str, face_index: int = 0, lang: str = "en"):
    """Deletes a face from a body (Direct Modeling)."""
    try:
        res = execute_fusion_script(build_delete_face_script(), {"body": body, "face_index": face_index}, use_common=["find_body"])
        val = get_result_value(res)
        err = map_result_error(val, lang, GEOMETRY_ERROR_MAP)
        if err: return err
        return f"Face {face_index} of '{body}' deleted."
    except FusionBridgeError as e: return bridge_error_message(e)

def extrude_sketch_logic(sketch_name: str, distance: float, lang: str = "en", offset: float = 0, op: str = "NewBody", profile_index: int = None, target_body: str = None, component_name: str = None, component_path: str = None):
    """Extrudes profiles of a sketch."""
    try:
        res = execute_fusion_script(build_extrude_sketch_script(), {"sketch": sketch_name, "dist": distance, "offset": offset, "op": op, "profile_index": profile_index, "target_body": target_body, "component_name": component_name, "component_path": component_path}, use_common=["find_body"])
        val = get_result_value(res)
        err = map_result_error(val, lang, GEOMETRY_ERROR_MAP)
        if err: return err
        return format_response(lang, "extrusion_created", name=sketch_name)
    except FusionBridgeError as e: return bridge_error_message(e)

def create_chamfer_logic(body: str, distance: float, lang: str = "en"):
    """Creates chamfers on a body."""
    try:
        res = execute_fusion_script(build_create_chamfer_script(), {"body": body, "dist": distance}, use_common=["find_body"])
        val = get_result_value(res)
        err = map_result_error(val, lang, GEOMETRY_ERROR_MAP)
        if err: return err
        return format_response(lang, "chamfer_created")
    except FusionBridgeError as e: return bridge_error_message(e)

def create_shell_logic(body: str, thickness: float, lang: str = "en"):
    """Creates a shell."""
    try:
        res = execute_fusion_script(build_create_shell_script(), {"body": body, "thick": thickness}, use_common=["find_body"])
        val = get_result_value(res)
        err = map_result_error(val, lang, GEOMETRY_ERROR_MAP)
        if err: return err
        return format_response(lang, "shell_created")
    except FusionBridgeError as e: return bridge_error_message(e)

def apply_3d_features_logic(operations: list[dict], lang: str = "en"):
    """
    Applies multiple 3D geometry features in a single batch.
    Supported actions include creation and corrective body edits such as extrude,
    fillet, chamfer, combine, create_box, create_cylinder, create_sphere,
    delete_body, rename_body, move_body, move_body_absolute, scale_body,
    shell, split_body, delete_face, offset_face, move_face, edit_feature,
    and delete_feature.
    Each operation should be a dict with 'action' or 'type' and required parameters.
    """
    try:
        res = execute_fusion_script(build_apply_3d_features_script(), {"operations": operations}, use_common=["find_body"])
        val = str(get_result_value(res))
        parts = val.split(",")
        errors = []
        successes = []
        
        for p in parts:
            if ":ERR" in p or "ERR_" in p:
                errors.append(p)
            elif ":OK" in p or p == "OK":
                successes.append(p)
            else:
                if p.startswith("ERR_"):
                    errors.append(p)

        if errors:
            mapped_errors = []
            for e in errors:
                found_mapping = False
                for code, message in GEOMETRY_ERROR_MAP.items():
                    if code in e:
                        mapped_errors.append(f"{e} -> {message if isinstance(message, str) else message.get('key', code)}")
                        found_mapping = True
                        break
                if not found_mapping:
                    mapped_errors.append(e)
            return f"Error: Some operations failed: {'; '.join(mapped_errors)}"
        
        if not successes and val != "OK":
             return f"Error: No successful operations. Result: {val}"

        return format_response(lang, "geometry_updated")
    except FusionBridgeError as e: return bridge_error_message(e)

def register_geometry_tools(mcp):
    register_tool(mcp, "apply_3d_features", apply_3d_features_logic)
    register_tool(mcp, "edit_feature", edit_feature_logic)
    register_tool(mcp, "delete_feature", delete_feature_logic)

def edit_feature_logic(feature_name: str, new_name: str = None, suppress: bool = None, value: str = None, lang: str = "en"):
    """Editiert ein bestehendes Feature (Name, Unterdrückung, Parameter)."""
    try:
        p = {"feature_name": feature_name}
        if new_name is not None: p["new_name"] = new_name
        if suppress is not None: p["suppress"] = suppress
        if value is not None: p["value"] = value
        
        res = execute_fusion_script(build_edit_feature_script(), p)
        val = str(get_result_value(res))

        if "OK" in val:

            return format_response(lang, "feature_updated", name=feature_name)
            
        err = map_result_error(val, lang, GEOMETRY_ERROR_MAP)
        if err: return err
        
        return f"Error: {val}"
    except FusionBridgeError as e: return bridge_error_message(e)

def delete_feature_logic(feature_name: str, lang: str = "en"):
    """Löscht ein bestehendes Feature."""
    try:
        res = execute_fusion_script(build_delete_feature_script(), {"feature_name": feature_name})
        val = str(get_result_value(res))
        
        if "OK" in val:
            return format_response(lang, "feature_deleted", name=feature_name)
            
        err = map_result_error(val, lang, GEOMETRY_ERROR_MAP)
        if err: return err
        
        return f"Error: {val}"
    except FusionBridgeError as e: return bridge_error_message(e)
