from core.bridge import execute_fusion_script, get_i18n_data, FusionBridgeError
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
I18N_PATH = os.path.join(BASE_DIR, "i18n.json")
I18N = get_i18n_data(I18N_PATH)

def export_stl_logic(filename: str):
    script = """
import os
d = adsk.fusion.Design.cast(app.activeProduct)
em = d.exportManager
# Sicherer Pfad im Home-Verzeichnis
path = os.path.join(os.path.expanduser('~'), params['filename'] + '.stl')
stl_opt = em.createSTLExportOptions(d.rootComponent, path)
em.execute(stl_opt)
returnValue.append(f"Exported to {path}")
"""
    try:
        res = execute_fusion_script(script, {"filename": filename})
        return res.get("data", ["Error"])[0]
    except FusionBridgeError as e:
        return str(e)

def export_f3d_logic(filename: str):
    script = """
import os
d = adsk.fusion.Design.cast(app.activeProduct)
em = d.exportManager
path = os.path.join(os.path.expanduser('~'), params['filename'] + '.f3d')
f3d_opt = em.createFusionArchiveExportOptions(path)
em.execute(f3d_opt)
returnValue.append(f"Project exported to {path}")
"""
    try:
        res = execute_fusion_script(script, {"filename": filename})
        return res.get("data", ["Error"])[0]
    except FusionBridgeError as e:
        return str(e)

def register_export_tools(mcp):
    # DEUTSCH
    de = I18N["de"]["tools"]
    @mcp.tool(name=de["export_stl"]["name"], description=de["export_stl"]["description"])
    def stl_exportieren(dateiname: str = "modell") -> str:
        return export_stl_logic(dateiname)

    @mcp.tool(name=de["export_f3d"]["name"], description=de["export_f3d"]["description"])
    def projekt_exportieren(dateiname: str = "archiv") -> str:
        return export_f3d_logic(dateiname)

    # ENGLISCH
    en = I18N["en"]["tools"]
    @mcp.tool(name=en["export_stl"]["name"], description=en["export_stl"]["description"])
    def export_stl(filename: str = "model") -> str:
        return export_stl_logic(filename)

    @mcp.tool(name=en["export_f3d"]["name"], description=en["export_f3d"]["description"])
    def export_project(filename: str = "archive") -> str:
        return export_f3d_logic(filename)
