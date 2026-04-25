from core.bridge import execute_fusion_script, get_i18n_data, FusionBridgeError
import os
import base64

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
I18N_PATH = os.path.join(BASE_DIR, "i18n.json")
I18N = get_i18n_data(I18N_PATH)

def capture_view_logic():
    script = """
import base64, os, tempfile
path = os.path.join(tempfile.gettempdir(), 'fusion_view.png')
app.activeViewport.saveAsImageFile(path, 800, 600)
with open(path, "rb") as f:
    data = base64.b64encode(f.read()).decode('utf-8')
returnValue.append(data)
"""
    try:
        res = execute_fusion_script(script)
        # Fix Finding 5: Return the base64 data
        return res.get("data", [""])[0]
    except FusionBridgeError as e:
        return str(e)

def get_body_info_logic():
    script = """
import json
c = app.activeProduct.rootComponent
info = []
for b in c.bRepBodies:
    info.append({"name": b.name, "volume": b.volume})
returnValue.append(json.dumps(info))
"""
    try:
        res = execute_fusion_script(script)
        return res.get("data", ["[]"])[0]
    except FusionBridgeError as e:
        return str(e)

def register_analysis_tools(mcp):
    # DEUTSCH
    de = I18N["de"]["tools"]
    @mcp.tool(name=de["capture_view"]["name"], description=de["capture_view"]["description"])
    def ansicht_fotografieren() -> str:
        return capture_view_logic()

    @mcp.tool(name=de["get_body_info"]["name"], description=de["get_body_info"]["description"])
    def koerper_analysieren() -> str:
        return get_body_info_logic()

    # ENGLISCH
    en = I18N["en"]["tools"]
    @mcp.tool(name=en["capture_view"]["name"], description=en["capture_view"]["description"])
    def capture_view() -> str:
        return capture_view_logic()

    @mcp.tool(name=en["get_body_info"]["name"], description=en["get_body_info"]["description"])
    def analyze_bodies() -> str:
        return get_body_info_logic()
