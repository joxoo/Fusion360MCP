from core.bridge import execute_fusion_script, get_i18n_data, FusionBridgeError
from core.utils import get_tool_definition, format_response
import os
import json

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
I18N = get_i18n_data(os.path.join(BASE_DIR, "i18n.json"))

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
    def cap_de(): return capture_view_logic("de")
    def cap_en(): return capture_view_logic("en")
    de_cap, en_cap = get_tool_definition(I18N, "capture_view")
    if de_cap: mcp.tool(name=de_cap["name"], description=de_cap["description"])(cap_de)
    if en_cap: mcp.tool(name=en_cap["name"], description=en_cap["description"])(cap_en)

    def ana_de(): return analyze_bodies_logic("de")
    def ana_en(): return analyze_bodies_logic("en")
    de_ana, en_ana = get_tool_definition(I18N, "get_body_info")
    if de_ana: mcp.tool(name=de_ana["name"], description=de_ana["description"])(ana_de)
    if en_ana: mcp.tool(name=en_ana["name"], description=en_ana["description"])(ana_en)
