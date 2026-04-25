from core.bridge import execute_fusion_script, FusionBridgeError
from core.utils import register_tool
import json

def capture_view_logic(lang: str):
    """Captures a screenshot of the active viewport and returns Base64 data."""
    script = """
import base64, os, tempfile
try:
    view = app.activeViewport
    temp_dir = tempfile.gettempdir()
    file_path = os.path.join(temp_dir, 'fusion_screenshot.png')
    view.saveAsImageFile(file_path, 0, 0)
    with open(file_path, 'rb') as f:
        encoded = base64.b64encode(f.read()).decode('utf-8')
    os.remove(file_path)
    returnValue.append(encoded)
except Exception as e:
    returnValue.append(f"Error: {str(e)}")
"""
    try:
        res = execute_fusion_script(script)
        return res.get("data", ["Error"])[0]
    except FusionBridgeError as e: return f"Error: {str(e)}"

def analyze_bodies_logic(lang: str):
    """Analyzes physical properties of all bodies in the design."""
    script = """
import json
try:
    bodies_info = []
    for b in root.bRepBodies:
        bodies_info.append({
            "name": b.name,
            "volume": b.volume,
            "area": b.area,
            "visible": b.isVisible
        })
    returnValue.append(json.dumps(bodies_info))
except Exception as e:
    returnValue.append(f"Error: {str(e)}")
"""
    try:
        res = execute_fusion_script(script)
        return res.get("data", ["[]"])[0]
    except FusionBridgeError as e: return f"Error: {str(e)}"

def register_analysis_tools(mcp):
    register_tool(mcp, "capture_view", capture_view_logic)
    register_tool(mcp, "get_body_info", analyze_bodies_logic)
