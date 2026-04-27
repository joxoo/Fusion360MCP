def build_create_sphere_script() -> str:
    return """try:
    center = adsk.core.Point3D.create(params['x'], params['y'], params['z'])
    radius = params['r']
    sk = root.sketches.add(root.xYConstructionPlane)
    
    # Draw a semi-circle arc on the XY plane (vertical-ish)
    startPoint = adsk.core.Point3D.create(center.x, center.y + radius, center.z)
    endPoint = adsk.core.Point3D.create(center.x, center.y - radius, center.z)
    alongArcPoint = adsk.core.Point3D.create(center.x + radius, center.y, center.z)
    
    arc = sk.sketchCurves.sketchArcs.addByThreePoints(startPoint, alongArcPoint, endPoint)
    axisLine = sk.sketchCurves.sketchLines.addByTwoPoints(startPoint, endPoint)
    
    if sk.profiles.count > 0:
        prof = sk.profiles.item(0)
        revolves = root.features.revolveFeatures
        rev_in = revolves.createInput(prof, axisLine, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
        angle = adsk.core.ValueInput.createByReal(2 * math.pi)
        rev_in.setAngleExtent(False, angle)
        rev_feat = revolves.add(rev_in)
        body = rev_feat.bodies.item(0)
        body.name = params['name']
        returnValue.append(body.name)
    else:
        returnValue.append("ERR_SKETCH")
except Exception as e:
    returnValue.append(f"ERR_API:{str(e)}")"""


def build_create_torus_script() -> str:
    return """try:
    center = adsk.core.Point3D.create(params['x'], params['y'], params['z'])
    major_r = params['major_r']
    minor_r = params['minor_r']
    
    # Create sketch on XY plane
    sk = root.sketches.add(root.xYConstructionPlane)
    
    # Draw circle for cross section, offset by major radius
    circle_center = adsk.core.Point3D.create(center.x + major_r, center.y, center.z)
    sk.sketchCurves.sketchCircles.addByCenterRadius(circle_center, minor_r)
    
    # Axis for revolution (Z axis through center)
    axis_start = adsk.core.Point3D.create(center.x, center.y, center.z)
    axis_end = adsk.core.Point3D.create(center.x, center.y, center.z + 1.0)
    # We can use construction axis or a line
    axisLine = sk.sketchCurves.sketchLines.addByTwoPoints(axis_start, axis_end)
    
    if sk.profiles.count > 0:
        prof = sk.profiles.item(0)
        revolves = root.features.revolveFeatures
        rev_in = revolves.createInput(prof, axisLine, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
        angle = adsk.core.ValueInput.createByReal(2 * math.pi)
        rev_in.setAngleExtent(False, angle)
        rev_feat = revolves.add(rev_in)
        body = rev_feat.bodies.item(0)
        body.name = params['name']
        returnValue.append(body.name)
    else:
        returnValue.append("ERR_SKETCH")
except Exception as e:
    returnValue.append(f"ERR_API:{str(e)}")"""
