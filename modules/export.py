from core.bridge import execute_fusion_script, FusionBridgeError
from core.utils import register_tool

def export_stl_logic(filename: str = "model", lang: str = "en"):
    """Exports the model as STL for 3D printing."""
    script = """
import adsk.core, adsk.fusion, os, tempfile
try:
    design = adsk.fusion.Design.cast(app.activeProduct)
    exportMgr = design.exportManager
    name = params.get('filename', 'model')
    if not name.endswith('.stl'): name += '.stl'
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
        return res.get("data", ["Error"])[0]
    except FusionBridgeError as e: return f"Error: {str(e)}"

def export_project_logic(filename: str = "archive", lang: str = "en"):
    """Exports the full project as F3D archive."""
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
        return res.get("data", ["Error"])[0]
    except FusionBridgeError as e: return f"Error: {str(e)}"

def register_export_tools(mcp):
    register_tool(mcp, "export_stl", export_stl_logic)
    register_tool(mcp, "export_f3d", export_project_logic)
