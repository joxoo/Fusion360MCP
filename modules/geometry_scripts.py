def build_create_chamfer_script() -> str:
    return """try:
    target = find_body_recursive(root, params['body'])
    if target:
        edges = adsk.core.ObjectCollection.create()
        for e in target.edges: edges.add(e)
        chamfers = target.parentComponent.features.chamferFeatures
        c_in = chamfers.createInput(edges, True)
        c_in.setToEqualDistance(adsk.core.ValueInput.createByReal(params['dist']))
        chamfers.add(c_in)
        returnValue.append("OK")
    else: returnValue.append("ERROR")
except Exception as e:
    returnValue.append(f"ERR_API:{str(e)}")"""


def build_create_shell_script() -> str:
    return """try:
    target = find_body_recursive(root, params['body'])
    if target:
        face = next((f for f in target.faces if f.geometry.surfaceType == adsk.core.SurfaceTypes.PlaneSurfaceType), target.faces.item(0))
        faces = adsk.core.ObjectCollection.create(); faces.add(face)
        shells = target.parentComponent.features.shellFeatures
        s_in = shells.createInput(faces, False)
        s_in.insideThickness = adsk.core.ValueInput.createByReal(params['thick'])
        shells.add(s_in)
        returnValue.append("OK")
    else: returnValue.append("ERROR")
except Exception as e:
    returnValue.append(f"ERR_API:{str(e)}")"""


def build_mirror_body_script() -> str:
    return """try:
    target = find_body_recursive(root, params['body'])
    plane = {"XY": root.xYConstructionPlane, "XZ": root.xZConstructionPlane, "YZ": root.yZConstructionPlane}.get(params['plane'], root.xYConstructionPlane)
    if target:
        ents = adsk.core.ObjectCollection.create(); ents.add(target)
        mirrors = root.features.mirrorFeatures
        m_in = mirrors.createInput(ents, plane)
        mirrors.add(m_in)
        returnValue.append("OK")
    else: returnValue.append("ERROR")
except Exception as e:
    returnValue.append(f"ERR_API:{str(e)}")"""


def build_create_box_script() -> str:
    return """try:
    pt = adsk.core.Point3D.create(0, 0, 0)
    s = root.sketches.add(root.xYConstructionPlane)
    s.sketchCurves.sketchLines.addTwoPointRectangle(
        pt, adsk.core.Point3D.create(pt.x + params['l'], pt.y + params['w'], 0)
    )
    if s.profiles.count < 1:
        returnValue.append("ERR_NO_PROFILE")
    else:
        prof = s.profiles.item(0)
        box = root.features.extrudeFeatures.addSimple(
            prof,
            adsk.core.ValueInput.createByReal(params['h']),
            adsk.fusion.FeatureOperations.NewBodyFeatureOperation
        )
        body = box.bodies.item(0)
        translate_body(body, params['x'], params['y'], params['z'])
        body.name = params['name']
        returnValue.append(body.name)
except Exception as e:
    returnValue.append(f"ERR_API:{str(e)}")"""


def build_create_circular_pattern_script() -> str:
    return """try:
    target = find_body_recursive(root, params['body'])
    if target:
        ents = adsk.core.ObjectCollection.create()
        ents.add(target)
        axis = {"X": root.xAxis, "Y": root.yAxis, "Z": root.zAxis}.get(params['axis'], root.zAxis)
        patterns = root.features.circularPatternFeatures
        p_in = patterns.createInput(ents, axis)
        p_in.quantity = adsk.core.ValueInput.createByReal(params['count'])
        p_in.totalAngle = adsk.core.ValueInput.createByString("360 deg")
        patterns.add(p_in)
        returnValue.append("OK")
    else: returnValue.append("ERR_BODY")
except Exception as e:
    returnValue.append(f"ERR_API:{str(e)}")"""


def build_create_rectangular_pattern_script() -> str:
    return """try:
    target = find_body_recursive(root, params['body'])
    if target:
        ents = adsk.core.ObjectCollection.create()
        ents.add(target)
        patterns = root.features.rectangularPatternFeatures
        p_in = patterns.createInput(ents, root.xAxis, adsk.core.ValueInput.createByReal(params['cx']), adsk.core.ValueInput.createByReal(params['dx']), adsk.fusion.RectangularPatternSpacingTypes.SpacingRectangularPatternSpacingType)
        if params['cy'] > 1:
            p_in.directionTwo = root.yAxis
            p_in.quantityTwo = adsk.core.ValueInput.createByReal(params['cy'])
            p_in.distanceTwo = adsk.core.ValueInput.createByReal(params['dy'])
        patterns.add(p_in)
        returnValue.append("OK")
    else: returnValue.append("ERR_BODY")
except Exception as e:
    returnValue.append(f"ERR_API:{str(e)}")"""


def build_create_fillet_script() -> str:
    return """try:
    target = find_body_recursive(root, params['body'])
    if target:
        edges = adsk.core.ObjectCollection.create()
        for e in target.edges: edges.add(e)
        fillets = target.parentComponent.features.filletFeatures
        f_in = fillets.createInput()
        f_in.addConstantRadiusEdgeSet(edges, adsk.core.ValueInput.createByReal(params['r']), True)
        fillets.add(f_in)
        returnValue.append("OK")
    else: returnValue.append("ERR_BODY")
except Exception as e:
    returnValue.append(f"ERR_API:{str(e)}")"""


def build_extrude_sketch_script() -> str:
    return """try:
    s = next((sk for sk in root.sketches if sk.name == params['sketch']), None)
    if s and s.profiles.count > 0:
        prof = s.profiles.item(0)
        ext = root.features.extrudeFeatures.addSimple(
            prof, 
            adsk.core.ValueInput.createByReal(params['dist']), 
            adsk.fusion.FeatureOperations.NewBodyFeatureOperation
        )
        returnValue.append(ext.bodies.item(0).name)
    else: returnValue.append("ERR_SKETCH")
except Exception as e:
    returnValue.append(f"ERR_API:{str(e)}")"""


def build_create_hole_script() -> str:
    return """try:
    plane = get_offset_plane(root.xYConstructionPlane, params['z'])
    sketch = root.sketches.add(plane)
    center = adsk.core.Point3D.create(params['x'], params['y'], 0)
    sketch.sketchCurves.sketchCircles.addByCenterRadius(center, params['d'] / 20.0)
    if sketch.profiles.count < 1:
        returnValue.append("ERR_NO_PROFILE")
    else:
        extrudes = root.features.extrudeFeatures
        ext_in = extrudes.createInput(sketch.profiles.item(0), adsk.fusion.FeatureOperations.CutFeatureOperation)
        ext_in.setDistanceExtent(False, adsk.core.ValueInput.createByReal(1000.0))
        extrudes.add(ext_in)
        returnValue.append("OK")
except Exception as e:
    returnValue.append(f"ERR_API:{str(e)}")"""
