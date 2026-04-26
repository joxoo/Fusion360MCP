from core.bridge import execute_fusion_script, FusionBridgeError
from core.utils import register_tool
from modules.analysis_scripts import build_capture_view_script, build_analyze_bodies_script
import json

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
