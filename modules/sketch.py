from core.bridge import execute_fusion_script, FusionBridgeError
from core.utils import format_response, register_tool
from core.error_handler import (
    bridge_error_message,
    get_result_value,
    map_result_error,
    localized_error,
)
from modules.sketch_scripts import (
    build_create_sketch_script,
    build_add_constraint_script,
    build_draw_line_script,
    build_draw_circle_script,
    build_draw_rectangle_script,
    build_sketch_circular_pattern_script,
    build_sketch_rectangular_pattern_script,
    build_sketch_offset_script,
    build_draw_arc_script,
    build_draw_polygon_script,
    build_draw_spline_script,
    build_draw_slot_script,
    build_sketch_project_script,
    build_draw_sketch_text_script,
    build_draw_ellipse_script,
    build_sketch_mirror_script,
    build_sketch_trim_script,
    build_edit_sketch_script,
)

SKETCH_ERROR_MAP = {
    "ERR_SKETCH": localized_error("sketch_not_found"),
    "ERR_SKETCH_NOT_FOUND": localized_error("sketch_not_found"),
    "ERR_NOT_FOUND": "Error: Target body or sketch not found.",
}

def _handle_sketch_result(res, lang: str, success_key: str, **kwargs):
    val = get_result_value(res)
    err = map_result_error(val, lang, SKETCH_ERROR_MAP)
    if err:
        return err
    return format_response(lang, success_key, **kwargs)

def sketch_project_logic(sketch_name: str, body_name: str, lang: str = "en"):
    """Projects all edges of a body into a sketch."""
    try:
        res = execute_fusion_script(build_sketch_project_script(), {"sketch": sketch_name, "body": body_name}, use_common=["find_body"])
        return _handle_sketch_result(res, lang, "sketch_projected")
    except FusionBridgeError as e: return bridge_error_message(e)

def draw_sketch_text_logic(sketch_name: str, text: str, x: float, y: float, height: float = 1.0, font: str = "Arial", lang: str = "en"):
    """Adds text to a sketch."""
    try:
        res = execute_fusion_script(build_draw_sketch_text_script(), {"sketch": sketch_name, "text": text, "x": x, "y": y, "height": height, "font": font}, use_common=["find_body"])
        return _handle_sketch_result(res, lang, "text_added")
    except FusionBridgeError as e: return bridge_error_message(e)

def draw_ellipse_logic(sketch_name: str, cx: float, cy: float, mx: float, my: float, ox: float, oy: float, lang: str = "en"):
    """Draws an ellipse in a sketch."""
    try:
        res = execute_fusion_script(build_draw_ellipse_script(), {"sketch": sketch_name, "cx": cx, "cy": cy, "mx": mx, "my": my, "ox": ox, "oy": oy}, use_common=["find_body"])
        return _handle_sketch_result(res, lang, "ellipse_drawn")
    except FusionBridgeError as e: return bridge_error_message(e)

def sketch_mirror_logic(sketch_name: str, lang: str = "en"):
    """Placeholder for sketch mirroring (Complex API)."""
    try:
        res = execute_fusion_script(build_sketch_mirror_script(), {"sketch": sketch_name}, use_common=["find_body"])
        return _handle_sketch_result(res, lang, "mirror_logic_called")
    except FusionBridgeError as e: return bridge_error_message(e)

def sketch_trim_logic(sketch_name: str, x: float, y: float, lang: str = "en"):
    """Trims a curve segment at a point."""
    try:
        res = execute_fusion_script(build_sketch_trim_script(), {"sketch": sketch_name, "x": x, "y": y}, use_common=["find_body"])
        return _handle_sketch_result(res, lang, "trim_logic_called")
    except FusionBridgeError as e: return bridge_error_message(e)

def create_sketch_logic(
    plane_name: str = "XY",
    name: str = "Sketch1",
    lang: str = "en",
    body_name: str = None,
    face_index: int = 0,
    component_name: str = None,
    component_path: str = None,
):
    """Creates a new sketch on a specific plane or a body face."""
    try:
        res = execute_fusion_script(build_create_sketch_script(), {
            "plane": plane_name,
            "name": name,
            "body": body_name,
            "face_index": face_index,
            "component_name": component_name,
            "component_path": component_path,
        }, use_common=["find_body"])
        val = get_result_value(res)
        
        error_map = {
            "ERR_BODY_OR_FACE_NOT_FOUND": "Error: Target body or face index not found.",
            "ERR_COMPONENT": localized_error("component_not_found"),
            "ERR_VERIFICATION_FAILED": "Error: Sketch verification failed. The sketch was not created or cannot be found.",
        }
        err = map_result_error(val, lang, error_map)
        if err: return err
        
        return format_response(lang, "sketch_created", name=val)
    except FusionBridgeError as e: return bridge_error_message(e)

def add_constraint_logic(sketch_name: str, entity1_id: int = 0, entity2_id: int = 0, const_type: str = "Horizontal", lang: str = "en"):
    """Adds a geometric constraint to a sketch."""
    try:
        res = execute_fusion_script(build_add_constraint_script(), {"sketch":sketch_name, "c1":entity1_id, "c2":entity2_id, "type":const_type}, use_common=["find_body"])
        return _handle_sketch_result(res, lang, "constraint_added", type=const_type)
    except FusionBridgeError as e: return bridge_error_message(e)

def draw_line_logic(sketch_name: str, x1: float, y1: float, x2: float, y2: float, lang: str = "en"):
    """Draws a line in a specific sketch."""
    try:
        res = execute_fusion_script(build_draw_line_script(), {"sketch": sketch_name, "x1": x1, "y1": y1, "x2": x2, "y2": y2}, use_common=["find_body"])
        return _handle_sketch_result(res, lang, "line_drawn")
    except FusionBridgeError as e: return bridge_error_message(e)

def draw_circle_logic(sketch_name: str, x: float, y: float, radius: float, lang: str = "en"):
    """Draws a circle in a specific sketch."""
    try:
        res = execute_fusion_script(build_draw_circle_script(), {"sketch": sketch_name, "x": x, "y": y, "r": radius}, use_common=["find_body"])
        return _handle_sketch_result(res, lang, "circle_drawn")
    except FusionBridgeError as e: return bridge_error_message(e)

def draw_rectangle_logic(sketch_name: str, x1: float, y1: float, x2: float, y2: float, lang: str = "en"):
    """Draws a rectangle in a specific sketch."""
    try:
        res = execute_fusion_script(build_draw_rectangle_script(), {"sketch": sketch_name, "x1": x1, "y1": y1, "x2": x2, "y2": y2}, use_common=["find_body"])
        return _handle_sketch_result(res, lang, "rectangle_drawn")
    except FusionBridgeError as e: return bridge_error_message(e)

def create_sketch_circular_pattern_logic(sketch_name: str, center_x: float, center_y: float, count: int, lang: str = "en"):
    """Creates a circular pattern of all curves in a sketch using GeometricConstraints."""
    try:
        res = execute_fusion_script(build_sketch_circular_pattern_script(), {"sketch": sketch_name, "cx": center_x, "cy": center_y, "count": count}, use_common=["find_body"])
        val = get_result_value(res)
        
        error_map = {
            "ERR_EMPTY": localized_error("sketch_not_found"),
            "OK": localized_error("sketch_pattern_created"),
        }
        err = map_result_error(val, lang, error_map)
        if err: return err
        
        return _handle_sketch_result(res, lang, "sketch_pattern_created")
    except FusionBridgeError as e: return bridge_error_message(e)

def create_sketch_rectangular_pattern_logic(sketch_name: str, count_x: int, dist_x: float, count_y: int = 1, dist_y: float = 0, lang: str = "en"):
    """Creates a rectangular pattern of all curves in a sketch using GeometricConstraints and helper lines for direction."""
    try:
        res = execute_fusion_script(build_sketch_rectangular_pattern_script(), {"sketch": sketch_name, "cx": count_x, "dx": dist_x, "cy": count_y, "dy": dist_y}, use_common=["find_body"])
        val = get_result_value(res)
        
        error_map = {
            "ERR_EMPTY": localized_error("sketch_not_found"),
            "OK": localized_error("sketch_pattern_created"),
        }
        err = map_result_error(val, lang, error_map)
        if err: return err
        
        return _handle_sketch_result(res, lang, "sketch_pattern_created")
    except FusionBridgeError as e: return bridge_error_message(e)

def create_sketch_offset_logic(sketch_name: str, distance: float, lang: str = "en"):
    """Creates an offset of all curves in a sketch."""
    try:
        res = execute_fusion_script(build_sketch_offset_script(), {"sketch": sketch_name, "dist": distance}, use_common=["find_body"])
        val = get_result_value(res)
        
        error_map = {
            "ERR_EMPTY": localized_error("sketch_not_found"),
            "OK": localized_error("sketch_offset_created"),
        }
        err = map_result_error(val, lang, error_map)
        if err: return err
        
        return _handle_sketch_result(res, lang, "sketch_offset_created")
    except FusionBridgeError as e: return bridge_error_message(e)

def draw_arc_logic(sketch_name: str, cx: float, cy: float, sx: float, sy: float, angle: float, lang: str = "en"):
    """Draws an arc in a specific sketch."""
    try:
        res = execute_fusion_script(build_draw_arc_script(), {"sketch": sketch_name, "cx": cx, "cy": cy, "sx": sx, "sy": sy, "angle": angle}, use_common=["find_body"])
        return _handle_sketch_result(res, lang, "arc_drawn")
    except FusionBridgeError as e: return bridge_error_message(e)

def draw_polygon_logic(sketch_name: str, cx: float, cy: float, radius: float, sides: int, lang: str = "en"):
    """Draws a regular polygon in a sketch using individual lines for better profile detection."""
    try:
        res = execute_fusion_script(build_draw_polygon_script(), {"sketch": sketch_name, "cx": cx, "cy": cy, "r": radius, "sides": sides}, use_common=["find_body"])
        return _handle_sketch_result(res, lang, "polygon_drawn", sides=sides)
    except Exception as e: return f"Error: {str(e)}"

def draw_spline_logic(sketch_name: str, points_list: list, lang: str = "en"):
    """Draws a smooth curve through a list of points."""
    try:
        res = execute_fusion_script(build_draw_spline_script(), {"sketch": sketch_name, "pts": points_list}, use_common=["find_body"])
        return _handle_sketch_result(res, lang, "spline_drawn")
    except FusionBridgeError as e: return bridge_error_message(e)

def draw_slot_logic(sketch_name: str, x1: float, y1: float, x2: float, y2: float, width: float, lang: str = "en"):
    """Draws a slot in a sketch."""
    try:
        res = execute_fusion_script(build_draw_slot_script(), {"sketch": sketch_name, "x1": x1, "y1": y1, "x2": x2, "y2": y2, "w": width}, use_common=["find_body"])
        return _handle_sketch_result(res, lang, "slot_drawn")
    except FusionBridgeError as e: return bridge_error_message(e)

def edit_sketch_logic(sketch_name: str, operations: list[dict], lang: str = "en"):
    """
    Executes multiple drawing operations in a single sketch.
    Each operation should be a dict with an 'action' key and required parameters.
    Supported actions: draw_line, draw_circle, draw_rectangle, draw_polygon, add_constraint.
    """
    try:
        res = execute_fusion_script(build_edit_sketch_script(), {"sketch": sketch_name, "operations": operations}, use_common=["find_body"])
        return _handle_sketch_result(res, lang, "sketch_updated", name=sketch_name)
    except FusionBridgeError as e: return bridge_error_message(e)

def register_sketch_tools(mcp):
    register_tool(mcp, "create_sketch", create_sketch_logic)
    register_tool(mcp, "edit_sketch", edit_sketch_logic)
