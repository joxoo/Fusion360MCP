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
    sk, owner_comp, err = resolve_sketch_context(
        params['sketch'],
        params.get('component_name'),
        params.get('component_path')
    )
    if err == "ERR_COMPONENT":
        returnValue.append("ERR_COMPONENT")
    elif sk and sk.profiles.count > 0:
        prof = sk.profiles.item(0)
        forms = owner_comp.features.formFeatures
        # Using direct addExtrude
        form_feat = forms.addExtrude(prof, adsk.core.ValueInput.createByReal(params['dist']), adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
        returnValue.append(form_feat.bodies.item(0).name)
    else: returnValue.append("ERR_SKETCH")
except Exception as e:
    returnValue.append(f"ERR_API:{str(e)}")"""


def build_create_form_revolve_script() -> str:
    return """try:
    sk, owner_comp, err = resolve_sketch_context(
        params['sketch'],
        params.get('component_name'),
        params.get('component_path')
    )
    if err == "ERR_COMPONENT":
        returnValue.append("ERR_COMPONENT")
    elif sk and sk.profiles.count > 0:
        axis_entity = {"X": owner_comp.xConstructionAxis, "Y": owner_comp.yConstructionAxis, "Z": owner_comp.zConstructionAxis}.get(params['axis'], owner_comp.zConstructionAxis)
        prof = sk.profiles.item(0)
        forms = owner_comp.features.formFeatures
        angle = adsk.core.ValueInput.createByString(f"{params['angle']} deg")
        form_feat = forms.addRevolve(prof, axis_entity, angle, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
        returnValue.append(form_feat.bodies.item(0).name)
    else: returnValue.append("ERR_SKETCH")
except Exception as e:
    returnValue.append(f"ERR_API:{str(e)}")"""


def build_create_form_sweep_script() -> str:
    return """try:
    prof_sk, owner_comp, profile_err = resolve_sketch_context(
        params['profile_sketch'],
        params.get('component_name'),
        params.get('component_path')
    )
    path_sk, path_owner, path_err = resolve_sketch_context(
        params['path_sketch'],
        params.get('component_name'),
        params.get('component_path')
    )
    if profile_err == "ERR_COMPONENT" or path_err == "ERR_COMPONENT":
        returnValue.append("ERR_COMPONENT")
    elif prof_sk and path_sk and owner_comp != path_owner:
        returnValue.append("ERR_OWNER_MISMATCH")
    elif prof_sk and path_sk and prof_sk.profiles.count > 0 and path_sk.sketchCurves.count > 0:
        prof = prof_sk.profiles.item(0)
        path = owner_comp.features.createPath(path_sk.sketchCurves.item(0))
        forms = owner_comp.features.formFeatures
        form_feat = forms.addSweep(prof, path, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
        returnValue.append(form_feat.bodies.item(0).name)
    else: returnValue.append("ERR_INPUT")
except Exception as e:
    returnValue.append(f"ERR_API:{str(e)}")"""


def build_create_form_loft_script() -> str:
    return """try:
    sketches, owner_comp, err = resolve_multi_sketch_context(
        params['sketch_names'],
        params.get('component_name'),
        params.get('component_path')
    )
    if err == "ERR_COMPONENT":
        returnValue.append("ERR_COMPONENT")
    elif err == "ERR_OWNER_MISMATCH":
        returnValue.append("ERR_OWNER_MISMATCH")
    else:
        profiles = []
        for sk in sketches:
            if sk and sk.profiles.count > 0:
                profiles.append(sk.profiles.item(0))

        if len(profiles) < 2:
            returnValue.append("ERR_MIN_PROFILES")
        else:
            forms = owner_comp.features.formFeatures
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
    forms = root.features.formFeatures
    form_feat = forms.add()
    if not form_feat:
        returnValue.append("ERR_UNSUPPORTED")
    else:
        form_feat.deleteMe()
        returnValue.append("ERR_UNSUPPORTED")
except Exception as e:
    returnValue.append(f"ERR_API:{str(e)}")"""


def build_create_form_cylinder_script() -> str:
    return """try:
    forms = root.features.formFeatures
    form_feat = forms.add()
    if not form_feat:
        returnValue.append("ERR_UNSUPPORTED")
    else:
        form_feat.deleteMe()
        returnValue.append("ERR_UNSUPPORTED")
except Exception as e:
    returnValue.append(f"ERR_API:{str(e)}")"""


def build_create_form_plane_script() -> str:
    return """try:
    forms = root.features.formFeatures
    form_feat = forms.add()
    if not form_feat:
        returnValue.append("ERR_UNSUPPORTED")
    else:
        form_feat.deleteMe()
        returnValue.append("ERR_UNSUPPORTED")
except Exception as e:
    returnValue.append(f"ERR_API:{str(e)}")"""


def build_create_form_torus_script() -> str:
    return """try:
    forms = root.features.formFeatures
    form_feat = forms.add()
    if not form_feat:
        returnValue.append("ERR_UNSUPPORTED")
    else:
        form_feat.deleteMe()
        returnValue.append("ERR_UNSUPPORTED")
except Exception as e:
    returnValue.append(f"ERR_API:{str(e)}")"""
