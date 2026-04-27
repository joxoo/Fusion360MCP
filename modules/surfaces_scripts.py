def build_create_surface_cylinder_script() -> str:
    return """try:
    plane = {"XY": root.xYConstructionPlane, "XZ": root.xZConstructionPlane, "YZ": root.yZConstructionPlane}.get(params['plane'], root.xYConstructionPlane)
    center = adsk.core.Point3D.create(params['x'], params['y'], params['z'])
    sk = root.sketches.add(plane)
    circle = sk.sketchCurves.sketchCircles.addByCenterRadius(center, params['r'])
    path = root.features.createPath(circle)
    extrude_feats = root.features.extrudeFeatures
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
    center = adsk.core.Point3D.create(params['x'], params['y'], params['z'])
    # Sphere via Revolve of semi-circle path
    sk = root.sketches.add(root.xZConstructionPlane)
    start_pt = adsk.core.Point3D.create(params['x'], params['y'] + params['r'], params['z'])
    arc = sk.sketchCurves.sketchArcs.addByCenterStartSweep(center, start_pt, math.pi)
    path = root.features.createPath(arc)
    axis_line = sk.sketchCurves.sketchLines.addByTwoPoints(start_pt, adsk.core.Point3D.create(params['x'], params['y'] - params['r'], params['z']))
    revolve_feats = root.features.revolveFeatures
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
    # Torus via Revolve of circle path offset from axis
    center = adsk.core.Point3D.create(params['x'] + params['major_r'], params['y'], params['z'])
    sk = root.sketches.add(root.xZConstructionPlane)
    circle = sk.sketchCurves.sketchCircles.addByCenterRadius(center, params['minor_r'])
    path = root.features.createPath(circle)
    revolve_feats = root.features.revolveFeatures
    rev_in = revolve_feats.createInput(path, root.zConstructionAxis, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
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
    target = find_body_recursive(root, params['body'])
    tool_sk = next((s for s in root.sketches if s.name == params['tool_sketch']), None)
    
    if target and tool_sk and tool_sk.sketchCurves.count > 0:
        tool_curve = tool_sk.sketchCurves.item(0)
        trims = root.features.trimFeatures
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
        extends = root.features.extendFeatures
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
        reverses = root.features.reverseNormalFeatures
        r_in = reverses.createInput(faces)
        reverses.add(r_in)
        returnValue.append("OK")
    else: returnValue.append("ERR_BODY")
except Exception as e:
    returnValue.append(f"ERR_API:{str(e)}")"""


def build_create_surface_patch_script() -> str:
    return """try:
    sk = next((s for s in root.sketches if s.name == params['sketch']), None)
    if sk and sk.profiles.count > 0:
        prof = sk.profiles.item(0)
        patches = root.features.patchFeatures
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
        offsets = root.features.offsetFeatures
        o_in = offsets.createInput(faces, adsk.core.ValueInput.createByReal(params['dist']), adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
        off_feat = offsets.add(o_in)
        returnValue.append(off_feat.bodies.item(0).name)
    else: returnValue.append("ERR_BODY")
except Exception as e:
    returnValue.append(f"ERR_API:{str(e)}")"""


def build_stitch_surfaces_script() -> str:
    return """try:
    surfaces = adsk.core.ObjectCollection.create()
    for name in params['body_names']:
        b = find_body_recursive(root, name)
        if b: surfaces.add(b)
    
    if surfaces.count > 0:
        stitches = root.features.stitchFeatures
        s_in = stitches.createInput(surfaces, adsk.core.ValueInput.createByReal(params.get('tol', 0.1)), adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
        stitch_feat = stitches.add(s_in)
        returnValue.append(stitch_feat.bodies.item(0).name)
    else: returnValue.append("ERR_MIN_SURFACES")
except Exception as e:
    returnValue.append(f"ERR_API:{str(e)}")"""


def build_thicken_surface_script() -> str:
    return """try:
    target = find_body_recursive(root, params['body'])
    if target:
        # Get first face for thickening
        face = target.faces.item(0)
        thickens = root.features.thickenFeatures
        t_in = thickens.createInput(face, adsk.core.ValueInput.createByReal(params['thick']), False, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
        thick_feat = thickens.add(t_in)
        returnValue.append(thick_feat.bodies.item(0).name)
    else: returnValue.append("ERR_BODY")
except Exception as e:
    returnValue.append(f"ERR_API:{str(e)}")"""
