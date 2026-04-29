def build_cleanup_design_script() -> str:
    return """try:
    for i in range(root.occurrences.count - 1, -1, -1):
        root.occurrences.item(i).deleteMe()
    for i in range(root.bRepBodies.count - 1, -1, -1):
        root.bRepBodies.item(i).deleteMe()
    returnValue.append("OK")
except Exception as e:
    returnValue.append(f"ERR_API:{str(e)}")"""


def build_restart_mcp_script() -> str:
    return "start_mcp_server(); returnValue.append('OK')"


def build_create_new_design_script() -> str:
    return "app.documents.add(0); returnValue.append('OK')"


def build_manage_design_script() -> str:
    return """
import json, os
try:
    action = params.get('action', 'cleanup')
    if action == 'cleanup':
        # 1. Clear Occurrences (Components)
        for i in range(root.occurrences.count - 1, -1, -1):
            try: root.occurrences.item(i).deleteMe()
            except: pass
            
        # 2. Clear BRep Bodies
        for i in range(root.bRepBodies.count - 1, -1, -1):
            try: root.bRepBodies.item(i).deleteMe()
            except: pass

        # 3. Clear Mesh Bodies
        for i in range(root.meshBodies.count - 1, -1, -1):
            try: root.meshBodies.item(i).deleteMe()
            except: pass

        # 4. Clear Sketches
        for i in range(root.sketches.count - 1, -1, -1):
            try: root.sketches.item(i).deleteMe()
            except: pass

        # 5. Clear Construction Planes, Axes, Points
        for i in range(root.constructionPlanes.count - 1, -1, -1):
            try: root.constructionPlanes.item(i).deleteMe()
            except: pass
        for i in range(root.constructionAxes.count - 1, -1, -1):
            try: root.constructionAxes.item(i).deleteMe()
            except: pass
        for i in range(root.constructionPoints.count - 1, -1, -1):
            try: root.constructionPoints.item(i).deleteMe()
            except: pass

        # 6. Delete Timeline entries if possible (Reset Design)
        design = adsk.fusion.Design.cast(app.activeProduct)
        if design:
            timeline = design.timeline
            if timeline.count > 0:
                # Move to beginning and delete everything after current position is not easy via API
                # but we can try to delete all features
                for i in range(design.rootComponent.features.count -1, -1, -1):
                    try: design.rootComponent.features.item(i).deleteMe()
                    except: pass
        
        returnValue.append("OK")
    elif action == 'restart_mcp':
        start_mcp_server()
        returnValue.append("OK")
    elif action == 'create_new':
        app.documents.add(0)
        returnValue.append("OK")
    elif action == 'export_step':
        name = params.get('filename', 'model')
        if not name.endswith('.step'): name += '.step'
        path = os.path.join(os.path.expanduser("~"), "Downloads", name)
        adsk.fusion.Design.cast(app.activeProduct).exportManager.execute(adsk.fusion.Design.cast(app.activeProduct).exportManager.createSTEPExportOptions(path))
        returnValue.append(f"Exported to {path}")
    elif action == 'export_stl':
        name = params.get('filename', 'model')
        if not name.endswith('.stl'): name += '.stl'
        path = os.path.join(os.path.expanduser("~"), "Downloads", name)
        # Export the whole design as STL
        stl_options = adsk.fusion.Design.cast(app.activeProduct).exportManager.createSTLExportOptions(root, path)
        adsk.fusion.Design.cast(app.activeProduct).exportManager.execute(stl_options)
        returnValue.append(f"Exported to {path}")
    else:
        returnValue.append("ERR_UNKNOWN_ACTION")
except Exception as e:
    returnValue.append(f"ERR_API:{str(e)}")
"""


