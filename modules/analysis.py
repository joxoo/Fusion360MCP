from core.bridge import execute_fusion_script, FusionBridgeError
from core.utils import register_tool
from core.error_handler import (
    bridge_error_message,
    get_result_value,
    map_result_error,
    localized_error,
)
from modules.analysis_scripts import (
    build_analyze_design_script,
    build_capture_view_script,
    build_get_feature_history_script,
    build_get_scene_map_script,
    build_get_volumetric_properties_script,
    build_get_bounding_box_script,
)
import json

ANALYSIS_ERROR_MAP = {
    "ERR_BODY": localized_error("body_not_found"),
}

def get_feature_history_logic(lang: str = "en"):
    """Liefert die Historie der Konstruktions-Features (Timeline)."""
    try:
        res = execute_fusion_script(build_get_feature_history_script())
        return get_result_value(res)
    except FusionBridgeError as e: return bridge_error_message(e)

def analyze_design_logic(action: str = "validate", body: str = "", lang: str = "en"):
    """
    Performs various design analysis and inspection tasks.
    Supported actions: get_assembly_tree, get_feature_history, validate,
    scene_map, physical_data, bounding_box, capture_view, capture_side,
    interference_check.
    """
    try:
        res = execute_fusion_script(build_analyze_design_script(), {
            "action": action, 
            "body": body if body else None
        }, use_common=["find_body"])
        val = get_result_value(res)
        err = map_result_error(val, lang, ANALYSIS_ERROR_MAP)
        if err: return err
        return val
    except FusionBridgeError as e: return bridge_error_message(e)

def capture_view_logic(width: int = 1280, height: int = 720, lang: str = "en"):
    """Captures a viewport screenshot with optional resolution."""
    try:
        res = execute_fusion_script(build_analyze_design_script(), {
            "action": "capture_view",
            "width": width,
            "height": height
        })
        return get_result_value(res)
    except FusionBridgeError as e: return bridge_error_message(e)

def capture_side_logic(lang: str = "en"):
    """Captures a right-side orthographic screenshot (perfect for aerodynamic profiles)."""
    return analyze_design_logic(action="capture_side", lang=lang)

def register_analysis_tools(mcp):
    register_tool(mcp, "analyze_design", analyze_design_logic)
    register_tool(mcp, "capture_view", capture_view_logic)
    register_tool(mcp, "capture_side", capture_side_logic)
    register_tool(mcp, "get_feature_history", get_feature_history_logic)
