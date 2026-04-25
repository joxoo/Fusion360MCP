from core.bridge import execute_fusion_script, get_i18n_data, FusionBridgeError
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
I18N_PATH = os.path.join(BASE_DIR, "i18n.json")
I18N = get_i18n_data(I18N_PATH)

def export_stl_logic(filename: str):
    script = """
import adsk.core, adsk.fusion, os, tempfile
try:
    design = adsk.fusion.Design.cast(app.activeProduct)
    exportMgr = design.exportManager
    
    # Use user filename or default
    name = params.get('filename', 'model')
    if not name.endswith('.stl'): name += '.stl'
    
    # Export to downloads or temp
    path = os.path.expanduser("~/Downloads")
    if not os.path.exists(path): path = tempfile.gettempdir()
    full_path = os.path.join(path, name)
    
    stlOptions = exportMgr.createSTLExportOptions(design.rootComponent, full_path)
    exportMgr.execute(stlOptions)
    returnValue.append(f"Exported to {full_path}")
except Exception as e:
    returnValue.append(f"Error: {str(e)}")
"""
    try:
        res = execute_fusion_script(script, {"filename": filename})
        return res.get("data", ["Error: No data from bridge"])[0]
    except FusionBridgeError as e:
        return f"Bridge Error: {str(e)}"

def export_project_logic(filename: str):
    script = """
import adsk.core, adsk.fusion, os, tempfile
try:
    design = adsk.fusion.Design.cast(app.activeProduct)
    exportMgr = design.exportManager
    
    name = params.get('filename', 'archive')
    if not name.endswith('.f3d'): name += '.f3d'
    
    path = os.path.expanduser("~/Downloads")
    if not os.path.exists(path): path = tempfile.gettempdir()
    full_path = os.path.join(path, name)
    
    options = exportMgr.createFusionArchiveExportOptions(full_path)
    exportMgr.execute(options)
    returnValue.append(f"Project exported to {full_path}")
except Exception as e:
    returnValue.append(f"Error: {str(e)}")
"""
    try:
        res = execute_fusion_script(script, {"filename": filename})
        return res.get("data", ["Error: No data from bridge"])[0]
    except FusionBridgeError as e:
        return f"Bridge Error: {str(e)}"

def register_export_tools(mcp):
    de = I18N["de"]["tools"]
    en = I18N["en"]["tools"]

    @mcp.tool(name=de["export_stl"]["name"], description=de["export_stl"]["description"])
    def stl_exportieren(dateiname: str = "modell") -> str:
        return export_stl_logic(dateiname)

    @mcp.tool(name=en["export_stl"]["name"], description=en["export_stl"]["description"])
    def export_stl(filename: str = "model") -> str:
        return export_stl_logic(filename)

    @mcp.tool(name=de["export_f3d"]["name"], description=de["export_f3d"]["description"])
    def projekt_exportieren(dateiname: str = "archiv") -> str:
        return export_project_logic(dateiname)

    @mcp.tool(name=en["export_f3d"]["name"], description=en["export_f3d"]["description"])
    def export_project(filename: str = "archive") -> str:
        return export_project_logic(filename)
