from core.bridge import execute_fusion_script, FusionBridgeError
from core.utils import register_tool
from core.error_handler import (
    bridge_error_message,
    get_result_value,
    map_result_error,
    localized_error,
)
from modules.analysis_scripts import (
    build_capture_view_script,
    build_analyze_bodies_script,
    build_check_interference_script,
    build_create_draft_analysis_script,
    build_get_volumetric_properties_script,
    build_get_bounding_box_script,
    build_validate_model_script,
    build_get_scene_map_script,
    build_capture_standard_views_script,
    build_get_assembly_tree_script,
)
import json

ANALYSIS_ERROR_MAP = {
    "ERR_BODY": localized_error("body_not_found"),
    "ERR_MIN_BODIES": "Error: At least two bodies are required for interference analysis.",
}

def get_assembly_tree_logic(lang: str = "en"):
    """Returns a full hierarchical tree of components, bodies, and sketches."""
    try:
        res = execute_fusion_script(build_get_assembly_tree_script())
        return get_result_value(res, "{}")
    except FusionBridgeError as e: return bridge_error_message(e)

def capture_view_logic(lang: str = "en"):
    """Captures a viewport screenshot."""
    try:
        res = execute_fusion_script(build_capture_view_script())
        return get_result_value(res)
    except FusionBridgeError as e: return bridge_error_message(e)

def capture_standard_views_logic(lang: str = "en"):
    """Captures four standard views (Top, Front, Right, ISO) and returns them as a set of images."""
    try:
        res = execute_fusion_script(build_capture_standard_views_script())
        val = get_result_value(res, "{}")
        if val.startswith("ERR_"): return val
        return val # JSON containing 4 base64 images
    except FusionBridgeError as e: return bridge_error_message(e)

def analyze_bodies_logic(lang: str = "en"):
    """Analyzes physical properties of all bodies in the design."""
    try:
        res = execute_fusion_script(build_analyze_bodies_script())
        return get_result_value(res)
    except FusionBridgeError as e: return bridge_error_message(e)

def check_interference_logic(body_names: list, include_coincident: bool = False, lang: str = "en"):
    """Checks assembly for interferences."""
    try:
        res = execute_fusion_script(build_check_interference_script(), {"body_names": body_names, "include_coincident": include_coincident}, use_common=["find_body"])
        val = get_result_value(res)
        err = map_result_error(val, lang, ANALYSIS_ERROR_MAP)
        if err: return err
        
        count = int(val)
        if count == 0: return "No interferences detected."
        return f"Warning: Found {count} interferences. Bodies are overlapping!"
    except FusionBridgeError as e: return bridge_error_message(e)

def create_draft_analysis_logic(body: str, min_angle: float = 0.5, max_angle: float = 5.0, lang: str = "en"):
    """Performs a draft angle analysis."""
    try:
        res = execute_fusion_script(build_create_draft_analysis_script(), {"body": body, "min_angle": min_angle, "max_angle": max_angle}, use_common=["find_body"])
        val = get_result_value(res)
        err = map_result_error(val, lang, ANALYSIS_ERROR_MAP)
        if err: return err
        return f"Draft analysis '{val}' created."
    except FusionBridgeError as e: return bridge_error_message(e)

def get_volumetric_properties_logic(body: str, lang: str = "en"):
    """Retrieves mass and physical data."""
    try:
        res = execute_fusion_script(build_get_volumetric_properties_script(), {"body": body}, use_common=["find_body"])
        val = get_result_value(res, "{}")
        err = map_result_error(val, lang, ANALYSIS_ERROR_MAP)
        if err: return err
        return val
    except FusionBridgeError as e: return bridge_error_message(e)

def get_bounding_box_logic(body: str, lang: str = "en"):
    """Retrieves bounding box dimensions."""
    try:
        res = execute_fusion_script(build_get_bounding_box_script(), {"body": body}, use_common=["find_body"])
        val = get_result_value(res, "{}")
        err = map_result_error(val, lang, ANALYSIS_ERROR_MAP)
        if err: return err
        return val
    except FusionBridgeError as e: return bridge_error_message(e)

def get_scene_map_logic(lang: str = "en"):
    """Returns a spatial map of all bodies (Centroid + Bounding Box)."""
    try:
        res = execute_fusion_script(build_get_scene_map_script())
        val = get_result_value(res, "[]")
        if val.startswith("ERR_"): return val
        return val # JSON string is enough for the agent
    except FusionBridgeError as e: return bridge_error_message(e)

def validate_model_logic(lang: str = "en"):
    """Performs a comprehensive construction check (Manifold, Interference, Body Count)."""
    try:
        res = execute_fusion_script(build_validate_model_script())
        val = get_result_value(res, "{}")
        if val.startswith("ERR_"): return val
        
        data = json.loads(val)
        report = []
        report.append(f"Model Validation Report:")
        report.append(f"- Body Count: {data['body_count']}")
        report.append(f"- Single Solid: {'Yes' if data['is_single_solid'] else 'No (Warning: Multiple bodies detected)'}")
        report.append(f"- Interferences: {data['interferences']}")
        
        if data['manifold_issues']:
            report.append(f"- Manifold Issues: {', '.join(data['manifold_issues'])}")
        else:
            report.append("- Manifold Status: All bodies are closed solids.")
            
        if data['is_single_solid'] and data['interferences'] == 0 and not data['manifold_issues']:
            report.append("\n✅ Ready for Print: The model is a perfect solid.")
        else:
            report.append("\n⚠️ Action Required: Model has integrity issues that might affect 3D printing.")
            
        return "\n".join(report)
    except FusionBridgeError as e: return bridge_error_message(e)
    except Exception as e: return f"Error parsing report: {str(e)}"

def register_analysis_tools(mcp):
    register_tool(mcp, "capture_view", capture_view_logic)
    register_tool(mcp, "capture_standard_views", capture_standard_views_logic)
    register_tool(mcp, "get_body_info", analyze_bodies_logic)
    register_tool(mcp, "check_interference", check_interference_logic)
    register_tool(mcp, "create_draft_analysis", create_draft_analysis_logic)
    register_tool(mcp, "get_volumetric_properties", get_volumetric_properties_logic)
    register_tool(mcp, "get_bounding_box", get_bounding_box_logic)
    register_tool(mcp, "validate_model", validate_model_logic)
    register_tool(mcp, "get_scene_map", get_scene_map_logic)
    register_tool(mcp, "get_assembly_tree", get_assembly_tree_logic)
