def build_export_stl_script() -> str:
    return """import adsk.core, adsk.fusion, os, tempfile
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
    returnValue.append(f"Error: {str(e)}")"""


def build_export_project_script() -> str:
    return """import adsk.core, adsk.fusion, os, tempfile
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
    returnValue.append(f"Error: {str(e)}")"""
