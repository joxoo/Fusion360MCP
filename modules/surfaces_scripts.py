def build_create_surface_cylinder_script() -> str:
    return """try:
    target_comp = get_default_target_component(params)
    if not target_comp:
        returnValue.append("ERR_COMPONENT")
    else:
        plane = get_component_plane(target_comp, params['plane'])
        center = adsk.core.Point3D.create(params['x'], params['y'], params['z'])
        sk = target_comp.sketches.add(plane)
        circle = sk.sketchCurves.sketchCircles.addByCenterRadius(center, params['r'])
        path = target_comp.features.createPath(circle)
        extrude_feats = target_comp.features.extrudeFeatures
        ext_in = extrude_feats.createInput(path, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
        ext_in.isSolid = False
        ext_in.setDistanceExtent(False, adsk.core.ValueInput.createByReal(params['h']))
        ext_feat = extrude_feats.add(ext_in)
        body = ext_feat.bodies.item(0)
        body.name = params['name']
        returnValue.append(body.name)
except Exception as e:
    returnValue.append(f"ERR_API:{str(e)}")"""


def build_create_surface_sphere_script() -> str:
    return """import math
try:
    target_comp = get_default_target_component(params)
    if not target_comp:
        returnValue.append("ERR_COMPONENT")
    else:
        center = adsk.core.Point3D.create(params['x'], params['y'], params['z'])
        # Sphere via Revolve of semi-circle path
        sk = target_comp.sketches.add(target_comp.xZConstructionPlane)
        start_pt = adsk.core.Point3D.create(params['x'], params['y'] + params['r'], params['z'])
        arc = sk.sketchCurves.sketchArcs.addByCenterStartSweep(center, start_pt, math.pi)
        path = target_comp.features.createPath(arc)
        axis_line = sk.sketchCurves.sketchLines.addByTwoPoints(start_pt, adsk.core.Point3D.create(params['x'], params['y'] - params['r'], params['z']))
        revolve_feats = target_comp.features.revolveFeatures
        rev_in = revolve_feats.createInput(path, axis_line, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
        rev_in.isSolid = False
        rev_in.setAngleExtent(False, adsk.core.ValueInput.createByReal(2 * math.pi))
        rev_feat = revolve_feats.add(rev_in)
        body = rev_feat.bodies.item(0)
        body.name = params['name']
        returnValue.append(body.name)
except Exception as e:
    returnValue.append(f"ERR_API:{str(e)}")"""


def build_create_surface_torus_script() -> str:
    return """import math
try:
    target_comp = get_default_target_component(params)
    if not target_comp:
        returnValue.append("ERR_COMPONENT")
    else:
        # Torus via Revolve of circle path offset from axis
        center = adsk.core.Point3D.create(params['x'] + params['major_r'], params['y'], params['z'])
        sk = target_comp.sketches.add(target_comp.xZConstructionPlane)
        circle = sk.sketchCurves.sketchCircles.addByCenterRadius(center, params['minor_r'])
        path = target_comp.features.createPath(circle)
        revolve_feats = target_comp.features.revolveFeatures
        rev_in = revolve_feats.createInput(path, target_comp.zConstructionAxis, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
        rev_in.isSolid = False
        rev_in.setAngleExtent(False, adsk.core.ValueInput.createByReal(2 * math.pi))
        rev_feat = revolve_feats.add(rev_in)
        body = rev_feat.bodies.item(0)
        body.name = params['name']
        returnValue.append(body.name)
except Exception as e:
    returnValue.append(f"ERR_API:{str(e)}")"""


def build_trim_surface_script() -> str:
    return """try:
    target, owner_comp, body_err = resolve_body_context(
        params['body'],
        params.get('component_name'),
        params.get('component_path')
    )
    tool_sk, sketch_owner, sketch_err = resolve_sketch_context(
        params['tool_sketch'],
        params.get('component_name'),
        params.get('component_path')
    )

    if body_err == "ERR_COMPONENT" or sketch_err == "ERR_COMPONENT":
        returnValue.append("ERR_COMPONENT")
    elif target and tool_sk and owner_comp != sketch_owner:
        returnValue.append("ERR_OWNER_MISMATCH")
    elif target and tool_sk and tool_sk.sketchCurves.count > 0:
        tool_curve = tool_sk.sketchCurves.item(0)
        trims = owner_comp.features.trimFeatures
        t_in = trims.createInput(tool_curve)
        # Simplified: Select all cells that should be removed
        for cell in t_in.bRepCells:
            cell.isSelected = True
        trims.add(t_in)
        returnValue.append("OK")
    else: returnValue.append("ERR_INPUT")
except Exception as e:
    returnValue.append(f"ERR_API:{str(e)}")"""


def build_extend_surface_script() -> str:
    return """try:
    target = find_body_recursive(root, params['body'])
    if target and target.edges.count > 0:
        edges = adsk.core.ObjectCollection.create()
        # Use first edge for extension
        edges.add(target.edges.item(0))
        extends = target.parentComponent.features.extendFeatures
        e_in = extends.createInput(edges, adsk.core.ValueInput.createByReal(params['dist']), adsk.fusion.SurfaceExtendTypes.TangentSurfaceExtendType)
        extends.add(e_in)
        returnValue.append("OK")
    else: returnValue.append("ERR_BODY")
except Exception as e:
    returnValue.append(f"ERR_API:{str(e)}")"""


def build_reverse_surface_normal_script() -> str:
    return """try:
    target = find_body_recursive(root, params['body'])
    if target:
        faces = adsk.core.ObjectCollection.create()
        for f in target.faces: faces.add(f)
        reverses = target.parentComponent.features.reverseNormalFeatures
        r_in = reverses.createInput(faces)
        reverses.add(r_in)
        returnValue.append("OK")
    else: returnValue.append("ERR_BODY")
except Exception as e:
    returnValue.append(f"ERR_API:{str(e)}")"""


def build_create_surface_patch_script() -> str:
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
        patches = owner_comp.features.patchFeatures
        p_in = patches.createInput(prof, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
        patch_feat = patches.add(p_in)
        body = patch_feat.bodies.item(0)
        # Handle optional naming if we wanted to (test plan doesn't use it here)
        returnValue.append(body.name)
    else: returnValue.append("ERR_SKETCH")
except Exception as e:
    returnValue.append(f"ERR_API:{str(e)}")"""


def build_offset_surface_script() -> str:
    return """try:
    target = find_body_recursive(root, params['body'])
    if target:
        faces = adsk.core.ObjectCollection.create()
        for f in target.faces: faces.add(f)
        offsets = target.parentComponent.features.offsetFeatures
        o_in = offsets.createInput(faces, adsk.core.ValueInput.createByReal(params['dist']), adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
        off_feat = offsets.add(o_in)
        returnValue.append(off_feat.bodies.item(0).name)
    else: returnValue.append("ERR_BODY")
except Exception as e:
    returnValue.append(f"ERR_API:{str(e)}")"""


def build_stitch_surfaces_script() -> str:
    return """try:
    bodies, owner_comp, err = resolve_multi_body_context(
        params['body_names'],
        params.get('component_name'),
        params.get('component_path')
    )
    if err == "ERR_COMPONENT":
        returnValue.append("ERR_COMPONENT")
    elif err == "ERR_OWNER_MISMATCH":
        returnValue.append("ERR_OWNER_MISMATCH")
    else:
        surfaces = adsk.core.ObjectCollection.create()
        first_name = None
        for b in bodies:
            surfaces.add(b)
            if first_name is None:
                first_name = b.name

    if len(returnValue) == 0:
        if surfaces.count > 0:
            stitches = owner_comp.features.stitchFeatures
            s_in = stitches.createInput(surfaces, adsk.core.ValueInput.createByReal(params.get('tol', 0.1)), adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
            stitch_feat = stitches.add(s_in)
            if stitch_feat and stitch_feat.bodies and stitch_feat.bodies.count > 0:
                returnValue.append(stitch_feat.bodies.item(0).name)
            else:
                # A stitch on a single open body or a no-op stitch can succeed without creating a new result body.
                returnValue.append(first_name or "OK")
        else:
            returnValue.append("ERR_MIN_SURFACES")
except Exception as e:
    returnValue.append(f"ERR_API:{str(e)}")"""


def build_thicken_surface_script() -> str:
    return """try:
    target = find_body_recursive(root, params['body'])
    if target:
        # Get first face for thickening
        face = target.faces.item(0)
        thickens = target.parentComponent.features.thickenFeatures
        t_in = thickens.createInput(face, adsk.core.ValueInput.createByReal(params['thick']), False, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
        thick_feat = thickens.add(t_in)
        returnValue.append(thick_feat.bodies.item(0).name)
    else: returnValue.append("ERR_BODY")
except Exception as e:
    returnValue.append(f"ERR_API:{str(e)}")"""


def build_edit_surfaces_script() -> str:
    return """
try:
    results = []
    for op in params.get('operations', []):
        action = op.get('action')
        try:
            if action == 'patch':
                s, owner_comp, err = resolve_sketch_context(op['sketch'], op.get('component_name'), op.get('component_path'))
                if s and s.profiles.count > 0:
                    patches = owner_comp.features.patchFeatures
                    p_in = patches.createInput(s.profiles.item(0), adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
                    p_feat = patches.add(p_in)
                    results.append(f"{action}:OK:{p_feat.bodies.item(0).name}")
                else: results.append(f"{action}:ERR_SKETCH")
            elif action == 'offset':
                target = find_body_recursive(root, op['body'])
                if target:
                    faces = adsk.core.ObjectCollection.create()
                    for f in target.faces: faces.add(f)
                    offsets = target.parentComponent.features.offsetFeatures
                    o_in = offsets.createInput(faces, adsk.core.ValueInput.createByReal(op['dist']), adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
                    o_feat = offsets.add(o_in)
                    results.append(f"{action}:OK:{o_feat.bodies.item(0).name}")
                else: results.append(f"{action}:ERR_BODY")
            elif action == 'stitch':
                tools = adsk.core.ObjectCollection.create()
                for name in op['body_names']:
                    t = find_body_recursive(root, name)
                    if t: tools.add(t)
                if tools.count > 0:
                    stitches = tools.item(0).parentComponent.features.stitchFeatures
                    s_in = stitches.createInput(tools, adsk.core.ValueInput.createByReal(op.get('tol', 0.1)), adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
                    s_feat = stitches.add(s_in)
                    results.append(f"{action}:OK:{s_feat.bodies.item(0).name}")
                else: results.append(f"{action}:ERR_MIN_SURFACES")
            elif action == 'thicken':
                target = find_body_recursive(root, op['body'])
                if target:
                    thickens = target.parentComponent.features.thickenFeatures
                    face = target.faces.item(0)
                    t_in = thickens.createInput(face, adsk.core.ValueInput.createByReal(op['thick']), False, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
                    t_feat = thickens.add(t_in)
                    results.append(f"{action}:OK:{t_feat.bodies.item(0).name}")
                else: results.append(f"{action}:ERR_BODY")
            else:
                results.append(f"{action}:ERR_UNKNOWN_ACTION")
        except Exception as e:
            results.append(f"{action}:ERR:{str(e)}")
    returnValue.append(",".join(results) if results else "OK")
except Exception as e:
    returnValue.append(f"ERR_API:{str(e)}")
"""

