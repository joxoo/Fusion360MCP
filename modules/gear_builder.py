def build_spur_gear_script() -> str:
    return """
import math
try:
    m = float(params['module'])
    n = int(params['num_teeth'])
    t = float(params['thickness'])
    pa = float(params['pa'])
    px = float(params['x'])
    py = float(params['y'])
    hd = float(params['hole_dia'])

    if m <= 0 or n < 4 or t <= 0:
        returnValue.append("ERR_PARAMS")
    else:
        dia_pitch = 10.0 / m
        pa_rad = pa * math.pi / 180.0
        pitch_dia = n / dia_pitch
        root_dia = pitch_dia - (2.0 * (1.25 / dia_pitch))
        base_dia = pitch_dia * math.cos(pa_rad)
        outer_dia = (n + 2.0) / dia_pitch
        root_rad = root_dia / 2.0
        outer_rad = outer_dia / 2.0
        center = adsk.core.Point3D.create(px, py, 0)

        def offset_point(local_x, local_y):
            return adsk.core.Point3D.create(px + local_x, py + local_y, 0)

        def involute_point(base_radius, dist_from_center):
            l = math.sqrt(dist_from_center * dist_from_center - base_radius * base_radius)
            alpha = l / base_radius
            theta = alpha - math.acos(base_radius / dist_from_center)
            return adsk.core.Point3D.create(
                dist_from_center * math.cos(theta),
                dist_from_center * math.sin(theta),
                0
            )

        base_sketch = root.sketches.add(root.xYConstructionPlane)
        base_sketch.sketchCurves.sketchCircles.addByCenterRadius(center, root_rad)
        if base_sketch.profiles.count < 1:
            returnValue.append("ERR_BASE_PROFILE")
        else:
            gear_ext = root.features.extrudeFeatures.addSimple(
                base_sketch.profiles.item(0),
                adsk.core.ValueInput.createByReal(t),
                adsk.fusion.FeatureOperations.NewBodyFeatureOperation
            )
            gear_base = gear_ext.bodies.item(0)

            tooth_sketch = root.sketches.add(root.xYConstructionPlane)
            involute_point_count = 10
            involute_radius = base_dia / 2.0
            radius_step = ((outer_dia - (involute_radius * 2.0)) / 2.0) / (involute_point_count - 1)
            involute_points = []
            for i in range(involute_point_count):
                involute_points.append(involute_point(base_dia / 2.0, involute_radius))
                involute_radius += radius_step

            pitch_involute_point = involute_point(base_dia / 2.0, pitch_dia / 2.0)
            pitch_point_angle = math.atan2(pitch_involute_point.y, pitch_involute_point.x)
            tooth_thickness_angle = -(2.0 * math.pi) / (2.0 * n)
            rot_angle = -pitch_point_angle + (tooth_thickness_angle / 2.0)
            cos_angle = math.cos(rot_angle)
            sin_angle = math.sin(rot_angle)

            rotated_points = []
            mirrored_points = []
            for pt in involute_points:
                rx = pt.x * cos_angle - pt.y * sin_angle
                ry = pt.x * sin_angle + pt.y * cos_angle
                rotated_points.append(offset_point(rx, ry))
                mirrored_points.append(offset_point(rx, -ry))

            point_set = adsk.core.ObjectCollection.create()
            for pt in rotated_points:
                point_set.add(pt)
            spline1 = tooth_sketch.sketchCurves.sketchFittedSplines.add(point_set)

            point_set = adsk.core.ObjectCollection.create()
            for pt in mirrored_points:
                point_set.add(pt)
            spline2 = tooth_sketch.sketchCurves.sketchFittedSplines.add(point_set)

            start1_local = rotated_points[0]
            start2_local = mirrored_points[0]
            root_point1 = offset_point(
                root_rad * math.cos(math.atan2(start1_local.y - py, start1_local.x - px)),
                root_rad * math.sin(math.atan2(start1_local.y - py, start1_local.x - px))
            )
            root_point2 = offset_point(
                root_rad * math.cos(math.atan2(start2_local.y - py, start2_local.x - px)),
                root_rad * math.sin(math.atan2(start2_local.y - py, start2_local.x - px))
            )
            tooth_sketch.sketchCurves.sketchLines.addByTwoPoints(root_point1, spline1.startSketchPoint)
            tooth_sketch.sketchCurves.sketchLines.addByTwoPoints(root_point2, spline2.startSketchPoint)

            outer_mid = offset_point(outer_rad, 0)
            tooth_sketch.sketchCurves.sketchArcs.addByThreePoints(spline1.endSketchPoint, outer_mid, spline2.endSketchPoint)

            root_mid = offset_point(root_rad, 0)
            tooth_sketch.sketchCurves.sketchArcs.addByThreePoints(root_point2, root_mid, root_point1)

            if tooth_sketch.profiles.count < 1:
                returnValue.append("ERR_TOOTH_PROFILE")
            else:
                tooth_ext = root.features.extrudeFeatures.addSimple(
                    tooth_sketch.profiles.item(0),
                    adsk.core.ValueInput.createByReal(t),
                    adsk.fusion.FeatureOperations.NewBodyFeatureOperation
                )
                tooth_body = tooth_ext.bodies.item(0)
                cyl_face = next((f for f in gear_base.faces if f.geometry.surfaceType == adsk.core.SurfaceTypes.CylinderSurfaceType), None)
                if not cyl_face:
                    returnValue.append("ERR_PATTERN_AXIS")
                else:
                    input_ents = adsk.core.ObjectCollection.create()
                    input_ents.add(tooth_body)
                    circ_input = root.features.circularPatternFeatures.createInput(input_ents, cyl_face)
                    circ_input.quantity = adsk.core.ValueInput.createByReal(n)
                    pattern_feat = root.features.circularPatternFeatures.add(circ_input)

                    tool_bodies = adsk.core.ObjectCollection.create()
                    tool_bodies.add(tooth_body)
                    if pattern_feat.bodies:
                        for i in range(pattern_feat.bodies.count):
                            tool_bodies.add(pattern_feat.bodies.item(i))

                    combine_input = root.features.combineFeatures.createInput(gear_base, tool_bodies)
                    combine_input.operation = adsk.fusion.FeatureOperations.JoinFeatureOperation
                    root.features.combineFeatures.add(combine_input)

                    if hd > 0:
                        hole_sketch = root.sketches.add(root.xYConstructionPlane)
                        hole_sketch.sketchCurves.sketchCircles.addByCenterRadius(center, hd / 20.0)
                        if hole_sketch.profiles.count > 0:
                            root.features.extrudeFeatures.addSimple(
                                hole_sketch.profiles.item(0),
                                adsk.core.ValueInput.createByReal(t),
                                adsk.fusion.FeatureOperations.CutFeatureOperation
                            )

                    gear_base.name = f"Gear_M{m}_Z{n}"
                    returnValue.append(gear_base.name)
except Exception as e:
    returnValue.append(f"ERR_API:{str(e)}")
"""
