from core.bridge import execute_fusion_script, FusionBridgeError
from core.utils import format_response, register_tool
from modules.geometry_scripts import (
    build_create_chamfer_script,
    build_create_shell_script,
    build_mirror_body_script,
    build_create_box_script,
    build_create_circular_pattern_script,
    build_create_rectangular_pattern_script,
    build_create_fillet_script,
    build_extrude_sketch_script,
    build_create_hole_script,
)

def create_chamfer_logic(body: str, distance: float, lang: str = "en"):
    """Adds a chamfer to all edges of a body."""
    try:
        res = execute_fusion_script(build_create_chamfer_script(), {"body":body, "dist":distance}, use_common=["find_body"])
        if res.get("data", [""])[0] == "ERROR": return format_response(lang, "body_not_found")
        return format_response(lang, "chamfer_created")
    except FusionBridgeError as e: return f"Error: {str(e)}"

def create_shell_logic(body: str, thickness: float, lang: str = "en"):
    """Hollows out a body with a given wall thickness."""
    try:
        res = execute_fusion_script(build_create_shell_script(), {"body":body, "thick":thickness}, use_common=["find_body"])
        if res.get("data", [""])[0] == "ERROR": return format_response(lang, "body_not_found")
        return format_response(lang, "shell_created")
    except FusionBridgeError as e: return f"Error: {str(e)}"

def mirror_body_logic(body: str, plane_name: str, lang: str = "en"):
    """Mirrors a body across a construction plane."""
    try:
        res = execute_fusion_script(build_mirror_body_script(), {"body":body, "plane":plane_name}, use_common=["find_body"])
        if res.get("data", [""])[0] == "ERROR": return format_response(lang, "body_not_found")
        return format_response(lang, "mirror_created")
    except FusionBridgeError as e: return f"Error: {str(e)}"

def create_box_logic(l: float, w: float, h: float, name: str, x: float = 0, y: float = 0, z: float = 0, op: str = "NewBody", taper: float = 0, lang: str = "en"):
    """Creates a basic box at specified coordinates."""
    try:
        res = execute_fusion_script(build_create_box_script(), {"l":l, "w":w, "h":h, "name":name, "x":x, "y":y, "z":z}, use_common=["placement"])
        val = res.get("data", [""])[0]
        if val == "ERR_NO_PROFILE": return format_response(lang, "sketch_not_found")
        if val.startswith("ERR_"): return val
        return format_response(lang, "box_created", name=val)
    except FusionBridgeError as e: return f"Error: {str(e)}"

def create_circular_pattern_logic(body_name: str, count: int, axis: str = "Z", lang: str = "en"):
    """Creates a circular pattern of a body around an axis (X, Y, Z)."""
    try:
        res = execute_fusion_script(build_create_circular_pattern_script(), {"body": body_name, "count": count, "axis": axis}, use_common=["find_body"])
        val = res.get("data", [""])[0]
        if val == "ERR_BODY": return format_response(lang, "body_not_found")
        return format_response(lang, "pattern_created")
    except FusionBridgeError as e: return f"Error: {str(e)}"

def create_rectangular_pattern_logic(body_name: str, count_x: int, dist_x: float, count_y: int = 1, dist_y: float = 0, lang: str = "en"):
    """Creates a rectangular pattern of a body."""
    try:
        res = execute_fusion_script(build_create_rectangular_pattern_script(), {"body": body_name, "cx": count_x, "dx": dist_x, "cy": count_y, "dy": dist_y}, use_common=["find_body"])
        val = res.get("data", [""])[0]
        if val == "ERR_BODY": return format_response(lang, "body_not_found")
        return format_response(lang, "pattern_created")
    except FusionBridgeError as e: return f"Error: {str(e)}"

def create_fillet_logic(body_name: str, radius: float, lang: str = "en"):
    """Adds a fillet to all edges of a body."""
    try:
        res = execute_fusion_script(build_create_fillet_script(), {"body": body_name, "r": radius}, use_common=["find_body"])
        val = res.get("data", [""])[0]
        if val == "ERR_BODY": return format_response(lang, "body_not_found")
        return format_response(lang, "fillet_created")
    except FusionBridgeError as e: return f"Error: {str(e)}"

def extrude_sketch_logic(sketch_name: str, distance: float, lang: str = "en"):
    """Extrudes the first profile of a sketch."""
    try:
        res = execute_fusion_script(build_extrude_sketch_script(), {"sketch": sketch_name, "dist": distance})
        val = res.get("data", [""])[0]
        if val == "ERR_SKETCH": return format_response(lang, "sketch_not_found")
        return format_response(lang, "extrusion_created", name=sketch_name)
    except FusionBridgeError as e: return f"Error: {str(e)}"

def create_hole_logic(diameter_mm: float, x: float = 0, y: float = 0, lang: str = "en", z: float = 0):
    """Creates a simple hole in the active design."""
    try:
        res = execute_fusion_script(build_create_hole_script(), {"d": diameter_mm, "x": x, "y": y, "z": z}, use_common=["placement"])
        val = res.get("data", [""])[0]
        if val == "OK": return format_response(lang, "hole_created")
        if val == "ERR_NO_PROFILE": return format_response(lang, "sketch_not_found")
        return f"Error: {val}"
    except FusionBridgeError as e: return f"Error: {str(e)}"

def register_geometry_tools(mcp):
    register_tool(mcp, "create_box", create_box_logic)
    register_tool(mcp, "create_hole", create_hole_logic)
    register_tool(mcp, "extrude_sketch", extrude_sketch_logic)
    register_tool(mcp, "create_circular_pattern", create_circular_pattern_logic)
    register_tool(mcp, "create_rectangular_pattern", create_rectangular_pattern_logic)
    register_tool(mcp, "create_chamfer", create_chamfer_logic)
    register_tool(mcp, "create_shell", create_shell_logic)
    register_tool(mcp, "create_fillet", create_fillet_logic)
    register_tool(mcp, "mirror_body", mirror_body_logic)
