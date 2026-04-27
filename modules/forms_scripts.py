def build_create_form_mirror_internal_script() -> str:
    return """try:
    target = find_tspline_body_recursive(root, params['body'])
    if target and target.objectType == adsk.fusion.TSplineBody.classType():
        form_feature = target.parentFormFeature
        form_feature.startEdit()
        # Requires two adjacent faces to define the plane. Defaulting to face 0 and 1.
        f1 = target.faces.item(0)
        f2 = target.faces.item(1)
        target.symmetries.addInternalMirrorSymmetry(f1, f2)
        form_feature.finishEdit()
        returnValue.append("OK")
    else: returnValue.append("ERR_NOT_A_FORM")
except Exception as e:
    returnValue.append(f"ERR_API:{str(e)}")"""


def build_clear_form_symmetry_script() -> str:
    return """try:
    target = find_tspline_body_recursive(root, params['body'])
    if target and target.objectType == adsk.fusion.TSplineBody.classType():
        form_feature = target.parentFormFeature
        form_feature.startEdit()
        target.symmetries.clearSymmetry()
        form_feature.finishEdit()
        returnValue.append("OK")
    else: returnValue.append("ERR_NOT_A_FORM")
except Exception as e:
    returnValue.append(f"ERR_API:{str(e)}")"""


def build_set_form_display_mode_script() -> str:
    return """try:
    target = find_tspline_body_recursive(root, params['body'])
    if target and target.objectType == adsk.fusion.TSplineBody.classType():
        form_feature = target.parentFormFeature
        form_feature.startEdit()
        ui.activeSelections.clear()
        ui.activeSelections.add(target)
        mode = params.get('mode', 'Smooth').lower()
        if mode == 'box': app.executeTextCommand(u'Commands.Start TSplineBoxDisplayCommand')
        else: app.executeTextCommand(u'Commands.Start TSplineSmoothDisplayCommand')
        form_feature.finishEdit()
        returnValue.append("OK")
    else: returnValue.append("ERR_NOT_A_FORM")
except Exception as e:
    returnValue.append(f"ERR_API:{str(e)}")"""


def build_bridge_form_entities_script() -> str:
    return """try:
    target = find_tspline_body_recursive(root, params['body'])
    if target and target.objectType == adsk.fusion.TSplineBody.classType():
        form_feature = target.parentFormFeature
        form_feature.startEdit()
        # Requires two edge sets. Defaulting to first few edges.
        ui.activeSelections.clear()
        ui.activeSelections.add(target.edges.item(0))
        ui.activeSelections.add(target.edges.item(target.edges.count // 2))
        app.executeTextCommand(u'Commands.Start TSplineBridgeCommand')
        app.executeTextCommand(u'NuCommands.CommitCmd')
        form_feature.finishEdit()
        returnValue.append("OK")
    else: returnValue.append("ERR_NOT_A_FORM")
except Exception as e:
    returnValue.append(f"ERR_API:{str(e)}")"""


def build_fill_form_hole_script() -> str:
    return """try:
    target = find_tspline_body_recursive(root, params['body'])
    if target and target.objectType == adsk.fusion.TSplineBody.classType():
        form_feature = target.parentFormFeature
        form_feature.startEdit()
        # Select an edge on the hole boundary
        ui.activeSelections.clear()
        ui.activeSelections.add(target.edges.item(0))
        app.executeTextCommand(u'Commands.Start TSplineFillHoleCommand')
        app.executeTextCommand(u'NuCommands.CommitCmd')
        form_feature.finishEdit()
        returnValue.append("OK")
    else: returnValue.append("ERR_NOT_A_FORM")
except Exception as e:
    returnValue.append(f"ERR_API:{str(e)}")"""


def build_convert_form_script() -> str:
    return """try:
    target = find_tspline_body_recursive(root, params['body'])
    if target and target.objectType == adsk.fusion.TSplineBody.classType():
        form_feature = target.parentFormFeature
        form_feature.startEdit()
        ui.activeSelections.clear()
        ui.activeSelections.add(target)
        # Convert T-Spline to B-Rep
        app.executeTextCommand(u'Commands.Start TSplineConvertCommand')
        app.executeTextCommand(u'NuCommands.CommitCmd')
        form_feature.finishEdit()
        returnValue.append("OK")
    else: returnValue.append("ERR_NOT_A_FORM")
except Exception as e:
    returnValue.append(f"ERR_API:{str(e)}")"""


def build_insert_form_edge_script() -> str:
    return """try:
    target = find_tspline_body_recursive(root, params['body'])
    if target and target.objectType == adsk.fusion.TSplineBody.classType():
        form_feature = target.parentFormFeature
        form_feature.startEdit()
        # Requires selecting an edge. Defaulting to first edge.
        edge = target.edges.item(0)
        # Using text command as high-level API for T-Spline editing is often restricted
        ui.activeSelections.clear()
        ui.activeSelections.add(edge)
        app.executeTextCommand(u'Commands.Start TSplineInsertEdgeCommand')
        app.executeTextCommand(u'NuCommands.CommitCmd')
        form_feature.finishEdit()
        returnValue.append("OK")
    else: returnValue.append("ERR_NOT_A_FORM")
except Exception as e:
    returnValue.append(f"ERR_API:{str(e)}")"""


def build_subdivide_form_face_script() -> str:
    return """try:
    target = find_tspline_body_recursive(root, params['body'])
    if target and target.objectType == adsk.fusion.TSplineBody.classType():
        form_feature = target.parentFormFeature
        form_feature.startEdit()
        face = target.faces.item(0)
        ui.activeSelections.clear()
        ui.activeSelections.add(face)
        app.executeTextCommand(u'Commands.Start TSplineSubdivideCommand')
        app.executeTextCommand(u'NuCommands.CommitCmd')
        form_feature.finishEdit()
        returnValue.append("OK")
    else: returnValue.append("ERR_NOT_A_FORM")
except Exception as e:
    returnValue.append(f"ERR_API:{str(e)}")"""


def build_create_form_crease_script() -> str:
    return """try:
    target = find_tspline_body_recursive(root, params['body'])
    if target and target.objectType == adsk.fusion.TSplineBody.classType():
        form_feature = target.parentFormFeature
        form_feature.startEdit()
        # Crease the first loop of edges
        edges = adsk.core.ObjectCollection.create()
        for i in range(min(5, target.edges.count)):
            edges.add(target.edges.item(i))
        ui.activeSelections.clear()
        for e in edges: ui.activeSelections.add(e)
        app.executeTextCommand(u'Commands.Start TSplineCreaseCommand')
        app.executeTextCommand(u'NuCommands.CommitCmd')
        form_feature.finishEdit()
        returnValue.append("OK")
    else: returnValue.append("ERR_NOT_A_FORM")
except Exception as e:
    returnValue.append(f"ERR_API:{str(e)}")"""


def build_create_form_extrude_script() -> str:
    return """try:
    sk = next((s for s in root.sketches if s.name == params['sketch']), None)
    if sk and sk.profiles.count > 0:
        prof = sk.profiles.item(0)
        forms = root.features.formFeatures
        # Using direct addExtrude
        form_feat = forms.addExtrude(prof, adsk.core.ValueInput.createByReal(params['dist']), adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
        returnValue.append(form_feat.bodies.item(0).name)
    else: returnValue.append("ERR_SKETCH")
except Exception as e:
    returnValue.append(f"ERR_API:{str(e)}")"""


def build_create_form_revolve_script() -> str:
    return """try:
    sk = next((s for s in root.sketches if s.name == params['sketch']), None)
    axis_entity = {"X": root.xConstructionAxis, "Y": root.yConstructionAxis, "Z": root.zConstructionAxis}.get(params['axis'], root.zConstructionAxis)
    if sk and sk.profiles.count > 0:
        prof = sk.profiles.item(0)
        forms = root.features.formFeatures
        angle = adsk.core.ValueInput.createByString(f"{params['angle']} deg")
        form_feat = forms.addRevolve(prof, axis_entity, angle, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
        returnValue.append(form_feat.bodies.item(0).name)
    else: returnValue.append("ERR_SKETCH")
except Exception as e:
    returnValue.append(f"ERR_API:{str(e)}")"""


def build_create_form_sweep_script() -> str:
    return """try:
    prof_sk = next((s for s in root.sketches if s.name == params['profile_sketch']), None)
    path_sk = next((s for s in root.sketches if s.name == params['path_sketch']), None)
    if prof_sk and path_sk and prof_sk.profiles.count > 0 and path_sk.sketchCurves.count > 0:
        prof = prof_sk.profiles.item(0)
        path = root.features.createPath(path_sk.sketchCurves.item(0))
        forms = root.features.formFeatures
        form_feat = forms.addSweep(prof, path, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
        returnValue.append(form_feat.bodies.item(0).name)
    else: returnValue.append("ERR_INPUT")
except Exception as e:
    returnValue.append(f"ERR_API:{str(e)}")"""


def build_create_form_loft_script() -> str:
    return """try:
    profiles = []
    for name in params['sketch_names']:
        sk = next((s for s in root.sketches if s.name == name), None)
        if sk and sk.profiles.count > 0:
            profiles.append(sk.profiles.item(0))
    
    if len(profiles) < 2:
        returnValue.append("ERR_MIN_PROFILES")
    else:
        forms = root.features.formFeatures
        # createLoftInput might work or we use addLoft
        f_in = forms.createLoftInput()
        for p in profiles:
            f_in.loftSections.add(p)
        form_feat = forms.add(f_in)
        returnValue.append(form_feat.bodies.item(0).name)
except Exception as e:
    returnValue.append(f"ERR_API:{str(e)}")"""


def build_create_form_box_script() -> str:
    return """try:
    forms = root.features.formFeatures
    form_feat = forms.add()
    if not form_feat:
        returnValue.append("ERR_UNSUPPORTED")
    else:
        # The public Python API exposes creating an empty form feature and importing TSM data,
        # but not primitive helpers like addBox in the current runtime.
        form_feat.deleteMe()
        returnValue.append("ERR_UNSUPPORTED")
except Exception as e:
    returnValue.append(f"ERR_API:{str(e)}")"""


def build_create_form_sphere_script() -> str:
    return """try:
    center = adsk.core.Point3D.create(params['x'], params['y'], params['z'])
    forms = root.features.formFeatures
    # addSphere(center, diameter, long_faces, lat_faces)
    form_feat = forms.addSphere(center, params['dia'], params.get('long_faces', 8), params.get('lat_faces', 8))
    returnValue.append(form_feat.bodies.item(0).name)
except Exception as e:
    returnValue.append(f"ERR_API:{str(e)}")"""


def build_create_form_cylinder_script() -> str:
    return """try:
    center = adsk.core.Point3D.create(params['x'], params['y'], params['z'])
    forms = root.features.formFeatures
    # addCylinder(center, radius, height, h_faces, d_faces)
    form_feat = forms.addCylinder(center, params['r'], params['h'], params.get('h_faces', 4), params.get('d_faces', 8))
    returnValue.append(form_feat.bodies.item(0).name)
except Exception as e:
    returnValue.append(f"ERR_API:{str(e)}")"""


def build_create_form_plane_script() -> str:
    return """try:
    center = adsk.core.Point3D.create(params['x'], params['y'], params['z'])
    forms = root.features.formFeatures
    # addPlane(center, length, width, l_faces, w_faces)
    form_feat = forms.addPlane(center, params['l'], params['w'], params.get('l_faces', 2), params.get('w_faces', 2))
    returnValue.append(form_feat.bodies.item(0).name)
except Exception as e:
    returnValue.append(f"ERR_API:{str(e)}")"""


def build_create_form_torus_script() -> str:
    return """try:
    center = adsk.core.Point3D.create(params['x'], params['y'], params['z'])
    forms = root.features.formFeatures
    # addTorus(center, major_r, minor_r, r_faces, p_faces)
    form_feat = forms.addTorus(center, params['major_r'], params['minor_r'], params.get('r_faces', 8), params.get('p_faces', 8))
    returnValue.append(form_feat.bodies.item(0).name)
except Exception as e:
    returnValue.append(f"ERR_API:{str(e)}")"""
