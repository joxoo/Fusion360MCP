from core.bridge import execute_fusion_script, FusionBridgeError
from core.utils import format_response, register_tool
from core.error_handler import (
    bridge_error_message,
    get_result_value,
    map_result_error,
    localized_error,
)
from modules.mesh_scripts import (
    build_import_mesh_script,
    build_tessellate_body_script,
    build_generate_face_groups_script,
    build_repair_mesh_script,
    build_convert_mesh_script,
    build_remesh_body_script,
    build_smooth_mesh_script,
    build_mesh_plane_cut_script,
)

MESH_ERROR_MAP = {
    "ERR_NOT_A_MESH": "Error: Target is not a mesh body.",
    "ERR_BODY": localized_error("body_not_found"),
    "ERR_INPUT": "Error: Mesh body or plane not found.",
    "ERR_FILE_NOT_FOUND": "Error: Mesh file not found.",
}

def remesh_body_logic(body: str, density: float = 0.5, lang: str = "en"):
    """Remeshes a mesh body with a given density (0.0 to 1.0)."""
    try:
        res = execute_fusion_script(build_remesh_body_script(), {"body": body, "density": density})
        val = get_result_value(res)
        err = map_result_error(val, lang, MESH_ERROR_MAP)
        if err: return err
        return f"Body '{body}' successfully remeshed."
    except FusionBridgeError as e: return bridge_error_message(e)

def smooth_mesh_logic(body: str, smoothing: float = 0.5, lang: str = "en"):
    """Smooths a mesh body (0.0 to 1.0)."""
    try:
        res = execute_fusion_script(build_smooth_mesh_script(), {"body": body, "smoothing": smoothing})
        val = get_result_value(res)
        err = map_result_error(val, lang, MESH_ERROR_MAP)
        if err: return err
        return f"Body '{body}' successfully smoothed."
    except FusionBridgeError as e: return bridge_error_message(e)

def mesh_plane_cut_logic(body: str, plane_name: str = "XY", fill_type: str = "MeshFill", lang: str = "en"):
    """Cuts a mesh body using a plane."""
    try:
        res = execute_fusion_script(build_mesh_plane_cut_script(), {"body": body, "plane": plane_name, "fill_type": fill_type})
        val = get_result_value(res)
        err = map_result_error(val, lang, MESH_ERROR_MAP)
        if err: return err
        return f"Mesh '{body}' successfully cut using {plane_name} plane."
    except FusionBridgeError as e: return bridge_error_message(e)

def generate_face_groups_logic(body: str, accurate: bool = True, lang: str = "en"):
    """Generates face groups on a mesh for prismatic conversion."""
    try:
        res = execute_fusion_script(build_generate_face_groups_script(), {"body": body, "type": 1 if accurate else 0})
        val = get_result_value(res)
        err = map_result_error(val, lang, MESH_ERROR_MAP)
        if err: return err
        return f"Face groups generated on '{body}'."
    except FusionBridgeError as e: return bridge_error_message(e)

def repair_mesh_logic(body: str, repair_type: str = "infoTypeDefault", lang: str = "en"):
    """Repairs a mesh body using various strategies."""
    try:
        res = execute_fusion_script(build_repair_mesh_script(), {"body": body, "repair_type": repair_type})
        val = get_result_value(res)
        err = map_result_error(val, lang, MESH_ERROR_MAP)
        if err: return err
        return f"Mesh '{body}' repair command executed."
    except FusionBridgeError as e: return bridge_error_message(e)

def convert_mesh_logic(body: str, conv_type: str = "infoPrismatic", lang: str = "en"):
    """Converts a mesh body to a solid (B-Rep)."""
    try:
        res = execute_fusion_script(build_convert_mesh_script(), {"body": body, "conv_type": conv_type})
        val = get_result_value(res)
        err = map_result_error(val, lang, MESH_ERROR_MAP)
        if err: return err
        return f"Mesh '{body}' successfully converted to solid."
    except FusionBridgeError as e: return bridge_error_message(e)

def import_mesh_logic(path: str, lang: str = "en"):
    """Imports an external mesh file (STL, OBJ, 3MF)."""
    try:
        res = execute_fusion_script(build_import_mesh_script(), {"path": path})
        val = get_result_value(res)
        error_map = {
            "ERR_FILE_NOT_FOUND": f"Error: Mesh file not found at {path}",
        }
        err = map_result_error(val, lang, error_map)
        if err: return err
        return f"Mesh file successfully imported into target component."
    except FusionBridgeError as e: return bridge_error_message(e)

def tessellate_body_logic(body: str, lang: str = "en"):
    """Converts a B-Rep body into a mesh (tessellation)."""
    try:
        res = execute_fusion_script(build_tessellate_body_script(), {"body": body}, use_common=["find_body"])
        val = get_result_value(res)
        err = map_result_error(val, lang, MESH_ERROR_MAP)
        if err: return err
        return f"Body '{body}' successfully tessellated into mesh data."
    except FusionBridgeError as e: return bridge_error_message(e)

def register_mesh_tools(mcp):
    register_tool(mcp, "import_mesh", import_mesh_logic)
    register_tool(mcp, "tessellate_body", tessellate_body_logic)
    register_tool(mcp, "generate_face_groups", generate_face_groups_logic)
    register_tool(mcp, "repair_mesh", repair_mesh_logic)
    register_tool(mcp, "convert_mesh", convert_mesh_logic)
    register_tool(mcp, "remesh_body", remesh_body_logic)
    register_tool(mcp, "smooth_mesh", smooth_mesh_logic)
    register_tool(mcp, "mesh_plane_cut", mesh_plane_cut_logic)
