from core.bridge import execute_fusion_script, FusionBridgeError
from core.utils import register_tool
from modules.analysis_scripts import (
    build_capture_view_script,
    build_analyze_bodies_script,
    build_check_interference_script,
    build_create_draft_analysis_script,
    build_get_volumetric_properties_script,
    build_get_bounding_box_script,
    build_validate_model_script,
    build_get_scene_map_script,
)
import json

def get_scene_map_logic(lang: str = "en"):
    """Returns a spatial map of all bodies (Centroid + Bounding Box)."""
    try:
        res = execute_fusion_script(build_get_scene_map_script())
        val = res.get("data", ["[]"])[0]
        if val.startswith("ERR_"): return val
        return val # JSON string is enough for the agent
    except FusionBridgeError as e: return f"Error: {str(e)}"

def validate_model_logic(lang: str = "en"):
    """Performs a comprehensive construction check (Manifold, Interference, Body Count)."""
    try:
        res = execute_fusion_script(build_validate_model_script())
        val = res.get("data", ["{}"])[0]
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
    except FusionBridgeError as e: return f"Error: {str(e)}"
    except Exception as e: return f"Error parsing report: {str(e)}"

def get_volumetric_properties_logic(body: str, lang: str = "en"):
    """Returns detailed mass, volume, and moments of inertia."""
    try:
        res = execute_fusion_script(build_get_volumetric_properties_script(), {"body": body}, use_common=["find_body"])
        val = res.get("data", ["{}"])[0]
        if val == "ERR_BODY": return "Error: Body not found."
        return val # Returns RAW JSON string
    except FusionBridgeError as e: return f"Error: {str(e)}"

def get_bounding_box_logic(body: str, lang: str = "en"):
    """Returns world-aligned bounding box dimensions."""
    try:
        res = execute_fusion_script(build_get_bounding_box_script(), {"body": body}, use_common=["find_body"])
        val = res.get("data", ["{}"])[0]
        if val == "ERR_BODY": return "Error: Body not found."
        return val # Returns RAW JSON string
    except FusionBridgeError as e: return f"Error: {str(e)}"

def check_interference_logic(body_names: list, include_coincident: bool = False, lang: str = "en"):
    """Checks for overlaps (interferences) between specified bodies."""
    try:
        res = execute_fusion_script(build_check_interference_script(), {
            "body_names": body_names, "include_coincident": include_coincident
        }, use_common=["find_body"])
        val = res.get("data", [""])[0]
        if val == "ERR_MIN_BODIES": return "Error: At least two bodies are required for interference check."
        if isinstance(val, str) and val.startswith("ERR_"): return val
        count = int(val)
        if count == 0: return "No interferences detected. The assembly fits perfectly."
        return f"Warning: Found {count} interferences. Bodies are overlapping!"
    except FusionBridgeError as e: return f"Error: {str(e)}"

def create_draft_analysis_logic(body: str, min_angle: float = 0.5, max_angle: float = 5.0, lang: str = "en"):
    """Creates a visual draft analysis for a body."""
    try:
        res = execute_fusion_script(build_create_draft_analysis_script(), {
            "body": body, "min_angle": min_angle, "max_angle": max_angle
        }, use_common=["find_body"])
        val = res.get("data", [""])[0]
        if val == "ERR_BODY": return "Error: Body not found."
        if isinstance(val, str) and val.startswith("ERR_"): return val
        return f"Draft analysis '{val}' created and active in Fusion 360."
    except FusionBridgeError as e: return f"Error: {str(e)}"

def capture_view_logic(lang: str = "en"):
    """Captures a screenshot of the active viewport and returns Base64 data."""
    try:
        res = execute_fusion_script(build_capture_view_script())
        return res.get("data", ["Error"])[0]
    except FusionBridgeError as e: return f"Error: {str(e)}"

def analyze_bodies_logic(lang: str = "en"):
    """Analyzes physical properties of all bodies in the design."""
    try:
        res = execute_fusion_script(build_analyze_bodies_script())
        return res.get("data", ["[]"])[0]
    except FusionBridgeError as e: return f"Error: {str(e)}"

def register_analysis_tools(mcp):
    register_tool(mcp, "capture_view", capture_view_logic)
    register_tool(mcp, "get_body_info", analyze_bodies_logic)
    register_tool(mcp, "check_interference", check_interference_logic)
    register_tool(mcp, "create_draft_analysis", create_draft_analysis_logic)
    register_tool(mcp, "get_volumetric_properties", get_volumetric_properties_logic)
    register_tool(mcp, "get_bounding_box", get_bounding_box_logic)
    register_tool(mcp, "validate_model", validate_model_logic)
    register_tool(mcp, "get_scene_map", get_scene_map_logic)
