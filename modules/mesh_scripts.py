def build_remesh_body_script() -> str:
    return """try:
    target = find_body_recursive(root, params['body'])
    if target and target.objectType == adsk.fusion.MeshBody.classType():
        ui.activeSelections.clear()
        ui.activeSelections.add(target)
        app.executeTextCommand(u'Commands.Start ParaMeshRemeshCommand')
        app.executeTextCommand(u'Commands.SetDouble infoDensity ' + str(params.get('density', 0.5)))
        app.executeTextCommand(u'NuCommands.CommitCmd')
        returnValue.append("OK")
    else: returnValue.append("ERR_NOT_A_MESH")
except Exception as e:
    returnValue.append(f"ERR_API:{str(e)}")"""


def build_smooth_mesh_script() -> str:
    return """try:
    target = find_body_recursive(root, params['body'])
    if target and target.objectType == adsk.fusion.MeshBody.classType():
        ui.activeSelections.clear()
        ui.activeSelections.add(target)
        app.executeTextCommand(u'Commands.Start ParaMeshSmoothCommand')
        app.executeTextCommand(u'Commands.SetDouble infoSmoothing ' + str(params.get('smoothing', 0.5)))
        app.executeTextCommand(u'NuCommands.CommitCmd')
        returnValue.append("OK")
    else: returnValue.append("ERR_NOT_A_MESH")
except Exception as e:
    returnValue.append(f"ERR_API:{str(e)}")"""


def build_mesh_plane_cut_script() -> str:
    return """try:
    target = find_body_recursive(root, params['body'])
    plane = {"XY": root.xYConstructionPlane, "XZ": root.xZConstructionPlane, "YZ": root.yZConstructionPlane}.get(params['plane'], root.xYConstructionPlane)
    
    if target and target.objectType == adsk.fusion.MeshBody.classType():
        ui.activeSelections.clear()
        ui.activeSelections.add(target)
        ui.activeSelections.add(plane)
        app.executeTextCommand(u'Commands.Start ParaMeshPlaneCutCommand')
        fill_type = params.get('fill_type', 'MeshFill')
        app.executeTextCommand(u'Commands.SetString infoFillType ' + fill_type)
        app.executeTextCommand(u'NuCommands.CommitCmd')
        returnValue.append("OK")
    else: returnValue.append("ERR_INPUT")
except Exception as e:
    returnValue.append(f"ERR_API:{str(e)}")"""


def build_generate_face_groups_script() -> str:
    return """try:
    target = find_body_recursive(root, params['body'])
    if target and target.objectType == adsk.fusion.MeshBody.classType():
        feats = root.features.meshGenerateFaceGroupsFeatures
        fg_in = feats.createInput(target)
        # 0: Fast, 1: Accurate
        fg_in.generationType = params.get('type', 1)
        feats.add(fg_in)
        returnValue.append("OK")
    else: returnValue.append("ERR_NOT_A_MESH")
except Exception as e:
    returnValue.append(f"ERR_API:{str(e)}")"""


def build_repair_mesh_script() -> str:
    return """try:
    target = find_body_recursive(root, params['body'])
    if target and target.objectType == adsk.fusion.MeshBody.classType():
        ui.activeSelections.clear()
        ui.activeSelections.add(target)
        # Using TextCommand as high-level API is limited for Repair
        app.executeTextCommand(u'Commands.Start ParaMeshRepairCommand')
        repair_type = params.get('repair_type', 'infoTypeDefault')
        app.executeTextCommand(u'Commands.SetString infoRepairType ' + repair_type)
        app.executeTextCommand(u'NuCommands.CommitCmd')
        returnValue.append("OK")
    else: returnValue.append("ERR_NOT_A_MESH")
except Exception as e:
    returnValue.append(f"ERR_API:{str(e)}")"""


def build_convert_mesh_script() -> str:
    return """try:
    target = find_body_recursive(root, params['body'])
    if target and target.objectType == adsk.fusion.MeshBody.classType():
        ui.activeSelections.clear()
        ui.activeSelections.add(target)
        # Using TextCommand for Prismatic conversion (requires Face Groups)
        app.executeTextCommand(u'Commands.Start Mesh2BRepCommand')
        conv_type = params.get('conv_type', 'infoPrismatic')
        app.executeTextCommand(u'Commands.SetString infoConversionType ' + conv_type)
        app.executeTextCommand(u'NuCommands.CommitCmd')
        returnValue.append("OK")
    else: returnValue.append("ERR_NOT_A_MESH")
except Exception as e:
    returnValue.append(f"ERR_API:{str(e)}")"""


def build_import_mesh_script() -> str:
    return """try:
    mesh_path = params['path']
    if os.path.exists(mesh_path):
        import_mgr = app.importManager
        mesh_options = import_mgr.createMeshImportOptions(mesh_path)
        # Use default units or provided ones
        unit_type = adsk.fusion.MeshImportUnits.MillimeterMeshImportUnits
        mesh_options.unitType = unit_type
        import_mgr.importToTarget(mesh_options, root)
        returnValue.append("OK")
    else: returnValue.append("ERR_FILE_NOT_FOUND")
except Exception as e:
    returnValue.append(f"ERR_API:{str(e)}")"""


def build_tessellate_body_script() -> str:
    return """try:
    target = find_body_recursive(root, params['body'])
    if target:
        # High quality tessellation
        mesh_mgr = target.meshManager
        calc = mesh_mgr.createMeshCalculator()
        calc.setQuality(adsk.fusion.TriangleMeshQualityOptions.HighQualityTriangleMesh)
        mesh_data = calc.calculate()
        
        # Create a visible mesh body
        mesh_bodies = root.meshBodies
        new_mesh = mesh_bodies.addByTriangleMeshData(
            mesh_data.nodeCoordinatesAsDouble, 
            mesh_data.nodeIndices, 
            mesh_data.normalVectorsAsDouble, 
            mesh_data.nodeIndices
        )
        new_mesh.name = target.name + "_Mesh"
        returnValue.append(new_mesh.name)
    else: returnValue.append("ERR_BODY")
except Exception as e:
    returnValue.append(f"ERR_API:{str(e)}")"""


def build_edit_mesh_script() -> str:
    return """
try:
    results = []
    for op in params.get('operations', []):
        action = op.get('action')
        target = find_body_recursive(root, op.get('body'))
        if not target or target.objectType != adsk.fusion.MeshBody.classType():
            results.append(f"{action}:ERR_NOT_A_MESH"); continue

        ui.activeSelections.clear()
        ui.activeSelections.add(target)
        try:
            if action == 'remesh':
                app.executeTextCommand(u'Commands.Start ParaMeshRemeshCommand')
                app.executeTextCommand(u'Commands.SetDouble infoDensity ' + str(op.get('density', 0.5)))
                app.executeTextCommand(u'NuCommands.CommitCmd')
                results.append(f"{action}:OK")
            elif action == 'smooth':
                app.executeTextCommand(u'Commands.Start ParaMeshSmoothCommand')
                app.executeTextCommand(u'Commands.SetDouble infoSmoothing ' + str(op.get('smoothing', 0.5)))
                app.executeTextCommand(u'NuCommands.CommitCmd')
                results.append(f"{action}:OK")
            elif action == 'repair':
                app.executeTextCommand(u'Commands.Start ParaMeshRepairCommand')
                app.executeTextCommand(u'Commands.SetString infoRepairType ' + op.get('repair_type', 'infoTypeDefault'))
                app.executeTextCommand(u'NuCommands.CommitCmd')
                results.append(f"{action}:OK")
            elif action == 'convert':
                app.executeTextCommand(u'Commands.Start Mesh2BRepCommand')
                app.executeTextCommand(u'Commands.SetString infoConversionType ' + op.get('conv_type', 'infoPrismatic'))
                app.executeTextCommand(u'NuCommands.CommitCmd')
                results.append(f"{action}:OK")
            else:
                results.append(f"{action}:ERR_UNKNOWN_ACTION")
        except Exception as e:
            results.append(f"{action}:ERR:{str(e)}")
    returnValue.append(",".join(results) if results else "OK")
except Exception as e:
    returnValue.append(f"ERR_API:{str(e)}")
"""

