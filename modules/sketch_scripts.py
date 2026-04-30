import json

def build_create_sketch_script() -> str:
    return """try:
    owner_comp, target_plane, err = resolve_sketch_creation_context(params)
    if err:
        returnValue.append(err)
    elif target_plane:
        owner_comp = activate_component_context(owner_comp)
        # Create sketch in the owner component of the target geometry
        s = owner_comp.sketches.add(target_plane)
        s.name = params['name']
        if find_sketch_recursive(root, s.name):
            returnValue.append(s.name)
        else:
            returnValue.append("ERR_VERIFICATION_FAILED")
    else:
        returnValue.append("ERR_CONTEXT_NOT_RESOLVED")
except Exception as e:
    returnValue.append(f"ERR_API:{str(e)}")"""


def build_add_constraint_script() -> str:
    return """try:
    s, owner, err = resolve_sketch_context(params['sketch'])
    if err:
        returnValue.append(err)
    elif s:
        returnValue.append("OK")
    else: returnValue.append("ERR_SKETCH_NOT_FOUND")
except Exception as e:
    returnValue.append(f"ERR_API:{str(e)}")"""


def build_draw_line_script() -> str:
    return """try:
    s, owner, err = resolve_sketch_context(params['sketch'])
    if err:
        returnValue.append(err)
    elif s:
        p1 = adsk.core.Point3D.create(params['x1'], params['y1'], 0)
        p2 = adsk.core.Point3D.create(params['x2'], params['y2'], 0)
        line = s.sketchCurves.sketchLines.addByTwoPoints(p1, p2)
        returnValue.append("OK")
    else: returnValue.append("ERR_SKETCH_NOT_FOUND")
except Exception as e:
    returnValue.append(f"ERR_API:{str(e)}")"""


def build_draw_circle_script() -> str:
    return """try:
    s, owner, err = resolve_sketch_context(params['sketch'])
    if err:
        returnValue.append(err)
    elif s:
        center = adsk.core.Point3D.create(params['x'], params['y'], 0)
        s.sketchCurves.sketchCircles.addByCenterRadius(center, params['r'])
        returnValue.append("OK")
    else: returnValue.append("ERR_SKETCH_NOT_FOUND")
except Exception as e:
    returnValue.append(f"ERR_API:{str(e)}")"""


def build_draw_rectangle_script() -> str:
    return """try:
    s, owner, err = resolve_sketch_context(params['sketch'])
    if err:
        returnValue.append(err)
    elif s:
        p1 = adsk.core.Point3D.create(params['x1'], params['y1'], 0)
        p2 = adsk.core.Point3D.create(params['x2'], params['y2'], 0)
        s.sketchCurves.sketchLines.addTwoPointRectangle(p1, p2)
        returnValue.append("OK")
    else: returnValue.append("ERR_SKETCH_NOT_FOUND")
except Exception as e:
    returnValue.append(f"ERR_API:{str(e)}")"""


def build_sketch_circular_pattern_script() -> str:
    return """try:
    s, owner, err = resolve_sketch_context(params['sketch'])
    if err:
        returnValue.append(err)
    elif s:
        entities = []
        for curve_type in [s.sketchCurves.sketchLines, s.sketchCurves.sketchCircles, s.sketchCurves.sketchArcs, s.sketchCurves.sketchFittedSplines]:
            for c in curve_type: entities.append(c)
        
        if len(entities) < 1:
            returnValue.append("ERR_EMPTY")
        else:
            center_point = s.sketchPoints.add(adsk.core.Point3D.create(params['cx'], params['cy'], 0))
            constraints = s.geometricConstraints
            pattern_input = constraints.createCircularPatternInput(entities, center_point)
            pattern_input.quantity = adsk.core.ValueInput.createByReal(params['count'])
            pattern_input.totalAngle = adsk.core.ValueInput.createByString("360 deg")
            constraints.addCircularPattern(pattern_input)
            returnValue.append("OK")
    else: returnValue.append("ERR_SKETCH_NOT_FOUND")
except Exception as e:
    returnValue.append(f"ERR_API:{str(e)}")"""


def build_sketch_rectangular_pattern_script() -> str:
    return """try:
    s, owner, err = resolve_sketch_context(params['sketch'])
    if err:
        returnValue.append(err)
    elif s:
        entities = []
        for curve_type in [s.sketchCurves.sketchLines, s.sketchCurves.sketchCircles, s.sketchCurves.sketchArcs, s.sketchCurves.sketchFittedSplines]:
            for c in curve_type: entities.append(c)
            
        if len(entities) < 1:
            returnValue.append("ERR_EMPTY")
        else:
            constraints = s.geometricConstraints
            pattern_input = constraints.createRectangularPatternInput(entities, adsk.fusion.PatternDistanceType.SpacingPatternDistanceType)
            
            lines = s.sketchCurves.sketchLines
            dir1 = next((l for l in lines if l.isConstruction), None)
            if not dir1:
                dir1 = lines.addByTwoPoints(adsk.core.Point3D.create(0,0,0), adsk.core.Point3D.create(1,0,0))
                dir1.isConstruction = True
            
            pattern_input.setDirectionOne(dir1, adsk.core.ValueInput.createByReal(params['cx']), adsk.core.ValueInput.createByReal(params['dx']))
            
            if params['cy'] > 1:
                dir2 = next((l for l in lines if l.isConstruction and l != dir1), None)
                if not dir2:
                    dir2 = lines.addByTwoPoints(adsk.core.Point3D.create(0,0,0), adsk.core.Point3D.create(0,1,0))
                    dir2.isConstruction = True
                pattern_input.setDirectionTwo(dir2, adsk.core.ValueInput.createByReal(params['cy']), adsk.core.ValueInput.createByReal(params['dy']))
            
            constraints.addRectangularPattern(pattern_input)
            returnValue.append("OK")
    else: returnValue.append("ERR_SKETCH_NOT_FOUND")
except Exception as e:
    returnValue.append(f"ERR_API:{str(e)}")"""


def build_sketch_offset_script() -> str:
    return """try:
    s, owner, err = resolve_sketch_context(params['sketch'])
    if err:
        returnValue.append(err)
    elif s:
        entities = adsk.core.ObjectCollection.create()
        for curve_type in [s.sketchCurves.sketchLines, s.sketchCurves.sketchCircles, s.sketchCurves.sketchArcs, s.sketchCurves.sketchFittedSplines]:
            for c in curve_type: entities.add(c)
        if entities.count < 1:
            returnValue.append("ERR_EMPTY")
        else:
            offset_point = adsk.core.Point3D.create(10.0, 10.0, 0)
            s.offset(entities, offset_point, params['dist'])
            returnValue.append("OK")
    else: returnValue.append("ERR_SKETCH_NOT_FOUND")
except Exception as e:
    returnValue.append(f"ERR_API:{str(e)}")"""


def build_draw_arc_script() -> str:
    return """try:
    s, owner, err = resolve_sketch_context(params['sketch'])
    if err:
        returnValue.append(err)
    elif s:
        center = adsk.core.Point3D.create(params['cx'], params['cy'], 0)
        start = adsk.core.Point3D.create(params['sx'], params['sy'], 0)
        angle = (params['angle'] * 3.14159) / 180.0
        s.sketchCurves.sketchArcs.addByCenterStartSweep(center, start, angle)
        returnValue.append("OK")
    else: returnValue.append("ERR_SKETCH_NOT_FOUND")
except Exception as e:
    returnValue.append(f"ERR_API:{str(e)}")"""


def build_draw_polygon_script() -> str:
    return """try:
    import math
    s, owner, err = resolve_sketch_context(params['sketch'])
    if err:
        returnValue.append(err)
    elif s:
        center_x = float(params['cx'])
        center_y = float(params['cy'])
        r = float(params['r'])
        n = int(params['sides'])
        points = []
        for i in range(n):
            angle = i * (2.0 * math.pi / n)
            px = center_x + r * math.cos(angle)
            py = center_y + r * math.sin(angle)
            points.append(adsk.core.Point3D.create(px, py, 0))
        for i in range(n):
            s.sketchCurves.sketchLines.addByTwoPoints(points[i], points[(i+1) % n])
        returnValue.append("OK")
    else:
        returnValue.append("ERR_SKETCH_NOT_FOUND")
except Exception as e:
    returnValue.append(f"ERR_API:{str(e)}")"""


def build_draw_spline_script() -> str:
    return """try:
    s, owner, err = resolve_sketch_context(params['sketch'])
    if err:
        returnValue.append(err)
    elif s:
        points = adsk.core.ObjectCollection.create()
        for p in params['pts']: points.add(adsk.core.Point3D.create(p[0], p[1], 0))
        s.sketchCurves.sketchFittedSplines.add(points)
        returnValue.append("OK")
    else: returnValue.append("ERR_SKETCH_NOT_FOUND")
except Exception as e:
    returnValue.append(f"ERR_API:{str(e)}")"""


def build_sketch_project_script() -> str:
    return """try:
    s, s_owner, s_err = resolve_sketch_context(params['sketch'])
    target_body, b_owner, b_err = resolve_body_context(params['body'])
    
    if s_err: returnValue.append(s_err)
    elif b_err: returnValue.append(b_err)
    elif s and target_body:
        # Project edges
        for edge in target_body.edges:
            s.project(edge)
        returnValue.append("OK")
    else: returnValue.append("ERR_NOT_FOUND")
except Exception as e:
    returnValue.append(f"ERR_API:{str(e)}")"""


def build_draw_sketch_text_script() -> str:
    return """try:
    s, owner, err = resolve_sketch_context(params['sketch'])
    if err:
        returnValue.append(err)
    elif s:
        texts = s.sketchTexts
        point = adsk.core.Point3D.create(params['x'], params['y'], 0)
        t_input = texts.createInput(params['text'], params['height'], point)
        t_input.fontName = params.get('font', 'Arial')
        texts.add(t_input)
        returnValue.append("OK")
    else: returnValue.append("ERR_SKETCH_NOT_FOUND")
except Exception as e:
    returnValue.append(f"ERR_API:{str(e)}")"""


def build_draw_ellipse_script() -> str:
    return """try:
    s, owner, err = resolve_sketch_context(params['sketch'])
    if err:
        returnValue.append(err)
    elif s:
        center = adsk.core.Point3D.create(params['cx'], params['cy'], 0)
        major = adsk.core.Point3D.create(params['mx'], params['my'], 0)
        on_ellipse = adsk.core.Point3D.create(params['ox'], params['oy'], 0)
        s.sketchCurves.sketchEllipses.add(center, major, on_ellipse)
        returnValue.append("OK")
    else: returnValue.append("ERR_SKETCH_NOT_FOUND")
except Exception as e:
    returnValue.append(f"ERR_API:{str(e)}")"""


def build_sketch_mirror_script() -> str:
    return """try:
    s, owner, err = resolve_sketch_context(params['sketch'])
    if err:
        returnValue.append(err)
    elif s:
        returnValue.append("ERR_NOT_IMPLEMENTED_DYNAMICALLY")
    else: returnValue.append("ERR_SKETCH_NOT_FOUND")
except Exception as e:
    returnValue.append(f"ERR_API:{str(e)}")"""


def build_sketch_trim_script() -> str:
    return """try:
    s, owner, err = resolve_sketch_context(params['sketch'])
    if err:
        returnValue.append(err)
    elif s:
        returnValue.append("ERR_REQUIRES_SPECIFIC_CURVE")
    else: returnValue.append("ERR_SKETCH_NOT_FOUND")
except Exception as e:
    returnValue.append(f"ERR_API:{str(e)}")"""


def build_draw_slot_script() -> str:
    return """try:
    s, owner, err = resolve_sketch_context(params['sketch'])
    if err:
        returnValue.append(err)
    elif s:
        p1 = adsk.core.Point3D.create(params['x1'], params['y1'], 0)
        p2 = adsk.core.Point3D.create(params['x2'], params['y2'], 0)
        sw = float(params['w']) / 10.0
        s.sketchCurves.sketchSlots.addCenterToCenterSlot(p1, p2, sw)
        returnValue.append("OK")
    else: returnValue.append("ERR_SKETCH_NOT_FOUND")
except Exception as e:
    returnValue.append(f"ERR_API:{str(e)}")"""


def build_edit_sketch_script() -> str:
    return """
import math
try:
    s, owner, err = resolve_sketch_context(params['sketch'], params.get('component_name'), params.get('component_path'))
    if err:
        returnValue.append(err)
    elif s:
        def editable_curves():
            curves = []
            for curve_group in (
                s.sketchCurves.sketchLines,
                s.sketchCurves.sketchCircles,
                s.sketchCurves.sketchArcs,
                s.sketchCurves.sketchEllipses,
                s.sketchCurves.sketchFittedSplines,
            ):
                for curve in curve_group:
                    curves.append(curve)
            return curves

        def get_curve(op):
            curves = editable_curves()
            idx = op.get('curve_index')
            if idx is None:
                curve_ref = op.get('curve_ref') or {}
                idx = curve_ref.get('curve_index')
            if idx is None:
                return None, "ERR_CURVE_INDEX_REQUIRED"
            if idx < 0 or idx >= len(curves):
                return None, "ERR_CURVE_NOT_FOUND"
            return curves[idx], None

        def get_selected_curves(op):
            curves = editable_curves()
            selected = []
            requested_indices = op.get('curve_indices')
            requested_refs = op.get('curve_refs') or []
            if requested_indices is None and requested_refs:
                requested_indices = [ref.get('curve_index') for ref in requested_refs]
            if not requested_indices:
                curve, curve_err = get_curve(op)
                if curve_err:
                    return None, curve_err
                return [curve], None
            for idx in requested_indices:
                if idx is None or idx < 0 or idx >= len(curves):
                    return None, "ERR_CURVE_NOT_FOUND"
                selected.append(curves[idx])
            return selected, None

        def editable_constraints():
            constraints = []
            for idx in range(s.geometricConstraints.count):
                constraints.append(s.geometricConstraints.item(idx))
            return constraints

        def get_constraint(op):
            constraints = editable_constraints()
            idx = op.get('constraint_index')
            if idx is None:
                constraint_ref = op.get('constraint_ref') or {}
                idx = constraint_ref.get('constraint_index')
            if idx is None:
                return None, "ERR_CONSTRAINT_INDEX_REQUIRED"
            if idx < 0 or idx >= len(constraints):
                return None, "ERR_CONSTRAINT_NOT_FOUND"
            return constraints[idx], None

        def editable_dimensions():
            dims = []
            for idx in range(s.sketchDimensions.count):
                dims.append(s.sketchDimensions.item(idx))
            return dims

        def get_dimension(op):
            dims = editable_dimensions()
            idx = op.get('dimension_index')
            if idx is None:
                dim_ref = op.get('dimension_ref') or {}
                idx = dim_ref.get('dimension_index')
            if idx is None:
                return None, "ERR_DIMENSION_INDEX_REQUIRED"
            if idx < 0 or idx >= len(dims):
                return None, "ERR_DIMENSION_NOT_FOUND"
            return dims[idx], None

        def get_curve_pair(op):
            curve_one, err_one = get_curve({"curve_index": op.get("curve_index"), "curve_ref": op.get("curve_ref")})
            if err_one:
                return None, None, err_one
            other_idx = op.get('other_curve_index')
            other_ref = op.get('other_curve_ref')
            curve_two, err_two = get_curve({"curve_index": other_idx, "curve_ref": other_ref})
            if err_two:
                return None, None, err_two
            return curve_one, curve_two, None

        def get_mirror_axis(op):
            axis_idx = op.get('mirror_curve_index')
            if axis_idx is None:
                axis_ref = op.get('mirror_curve_ref') or {}
                axis_idx = axis_ref.get('curve_index')
            if axis_idx is None:
                return None, "ERR_MIRROR_AXIS_REQUIRED"
            axis_curve, axis_err = get_curve({"curve_index": axis_idx})
            if axis_err:
                return None, axis_err
            if 'SketchLine' not in getattr(axis_curve, 'objectType', ''):
                return None, "ERR_MIRROR_AXIS_INVALID"
            return axis_curve, None

        def get_text_point(op):
            return adsk.core.Point3D.create(float(op.get('text_x', 0)), float(op.get('text_y', 0)), 0)

        def get_dimension_orientation(name):
            orientation_name = str(name or "aligned").lower()
            if orientation_name == "horizontal":
                return adsk.fusion.DimensionOrientations.HorizontalDimensionOrientation
            if orientation_name == "vertical":
                return adsk.fusion.DimensionOrientations.VerticalDimensionOrientation
            return adsk.fusion.DimensionOrientations.AlignedDimensionOrientation

        results = []
        for op in params.get('operations', []):
            action = op.get('action')
            try:
                if action == 'draw_line':
                    p1 = adsk.core.Point3D.create(op['x1'], op['y1'], 0)
                    p2 = adsk.core.Point3D.create(op['x2'], op['y2'], 0)
                    s.sketchCurves.sketchLines.addByTwoPoints(p1, p2)
                    results.append(f"{action}:OK")
                elif action == 'draw_circle':
                    center = adsk.core.Point3D.create(op['x'], op['y'], 0)
                    r = float(op.get('radius', op.get('r', 0)))
                    s.sketchCurves.sketchCircles.addByCenterRadius(center, r)
                    results.append(f"{action}:OK")
                elif action == 'draw_rectangle':
                    p1 = adsk.core.Point3D.create(op['x1'], op['y1'], 0)
                    p2 = adsk.core.Point3D.create(op['x2'], op['y2'], 0)
                    s.sketchCurves.sketchLines.addTwoPointRectangle(p1, p2)
                    results.append(f"{action}:OK")
                elif action == 'draw_polygon':
                    cx, cy = float(op['cx']), float(op['cy'])
                    r = float(op.get('radius', op.get('r', 0)))
                    n = int(op.get('sides', 6))
                    pts = [adsk.core.Point3D.create(cx + r*math.cos(i*2*math.pi/n), cy + r*math.sin(i*2*math.pi/n), 0) for i in range(n)]
                    for i in range(n): s.sketchCurves.sketchLines.addByTwoPoints(pts[i], pts[(i+1)%n])
                    results.append(f"{action}:OK")
                elif action == 'draw_arc':
                    center = adsk.core.Point3D.create(op['cx'], op['cy'], 0)
                    start = adsk.core.Point3D.create(op['sx'], op['sy'], 0)
                    angle = (float(op['angle']) * math.pi) / 180.0
                    s.sketchCurves.sketchArcs.addByCenterStartSweep(center, start, angle)
                    results.append(f"{action}:OK")
                elif action == 'draw_spline':
                    points = adsk.core.ObjectCollection.create()
                    for p in op['pts']:
                        points.add(adsk.core.Point3D.create(p[0], p[1], 0))
                    s.sketchCurves.sketchFittedSplines.add(points)
                    results.append(f"{action}:OK")
                elif action == 'draw_slot':
                    p1 = adsk.core.Point3D.create(op['x1'], op['y1'], 0)
                    p2 = adsk.core.Point3D.create(op['x2'], op['y2'], 0)
                    width = float(op.get('width', op.get('w', 0))) / 10.0
                    s.sketchCurves.sketchSlots.addCenterToCenterSlot(p1, p2, width)
                    results.append(f"{action}:OK")
                elif action == 'draw_ellipse':
                    center = adsk.core.Point3D.create(op['cx'], op['cy'], 0)
                    major = adsk.core.Point3D.create(op['mx'], op['my'], 0)
                    on_ellipse = adsk.core.Point3D.create(op['ox'], op['oy'], 0)
                    s.sketchCurves.sketchEllipses.add(center, major, on_ellipse)
                    results.append(f"{action}:OK")
                elif action == 'project_geometry':
                    body, body_owner, body_err = resolve_body_context(op['body'])
                    if body_err:
                        results.append(f"{action}:{body_err}")
                    elif body:
                        for edge in body.edges:
                            s.project(edge)
                        results.append(f"{action}:OK")
                    else:
                        results.append(f"{action}:ERR_BODY")
                elif action == 'offset':
                    entities = adsk.core.ObjectCollection.create()
                    selected = op.get('curve_indices')
                    curves = editable_curves()
                    if selected:
                        for idx in selected:
                            if idx < 0 or idx >= len(curves):
                                raise ValueError(f"curve index {idx} out of range")
                            entities.add(curves[idx])
                    else:
                        for curve in curves:
                            entities.add(curve)
                    if entities.count < 1:
                        results.append(f"{action}:ERR_EMPTY")
                    else:
                        offset_x = float(op.get('x', 10.0))
                        offset_y = float(op.get('y', 10.0))
                        s.offset(entities, adsk.core.Point3D.create(offset_x, offset_y, 0), float(op['dist']))
                        results.append(f"{action}:OK")
                elif action == 'circular_pattern':
                    curves = editable_curves()
                    if len(curves) < 1:
                        results.append(f"{action}:ERR_EMPTY")
                    else:
                        center_point = s.sketchPoints.add(adsk.core.Point3D.create(op['cx'], op['cy'], 0))
                        pattern_input = s.geometricConstraints.createCircularPatternInput(curves, center_point)
                        pattern_input.quantity = adsk.core.ValueInput.createByReal(op['count'])
                        pattern_input.totalAngle = adsk.core.ValueInput.createByString(op.get('total_angle', '360 deg'))
                        s.geometricConstraints.addCircularPattern(pattern_input)
                        results.append(f"{action}:OK")
                elif action == 'rectangular_pattern':
                    curves = editable_curves()
                    if len(curves) < 1:
                        results.append(f"{action}:ERR_EMPTY")
                    else:
                        pattern_input = s.geometricConstraints.createRectangularPatternInput(
                            curves,
                            adsk.fusion.PatternDistanceType.SpacingPatternDistanceType,
                        )
                        lines = s.sketchCurves.sketchLines
                        dir1 = next((l for l in lines if l.isConstruction), None)
                        if not dir1:
                            dir1 = lines.addByTwoPoints(adsk.core.Point3D.create(0,0,0), adsk.core.Point3D.create(1,0,0))
                            dir1.isConstruction = True
                        pattern_input.setDirectionOne(
                            dir1,
                            adsk.core.ValueInput.createByReal(op['count_x']),
                            adsk.core.ValueInput.createByReal(op['dist_x']),
                        )
                        count_y = int(op.get('count_y', 1))
                        if count_y > 1:
                            dir2 = next((l for l in lines if l.isConstruction and l != dir1), None)
                            if not dir2:
                                dir2 = lines.addByTwoPoints(adsk.core.Point3D.create(0,0,0), adsk.core.Point3D.create(0,1,0))
                                dir2.isConstruction = True
                            pattern_input.setDirectionTwo(
                                dir2,
                                adsk.core.ValueInput.createByReal(count_y),
                                adsk.core.ValueInput.createByReal(op.get('dist_y', 0)),
                            )
                        s.geometricConstraints.addRectangularPattern(pattern_input)
                        results.append(f"{action}:OK")
                elif action == 'delete_curve':
                    curve, curve_err = get_curve(op)
                    if curve_err:
                        results.append(f"{action}:{curve_err}")
                    else:
                        curve.deleteMe()
                        results.append(f"{action}:OK")
                elif action == 'move_entities':
                    selected_curves, curve_err = get_selected_curves(op)
                    if curve_err:
                        results.append(f"{action}:{curve_err}")
                    else:
                        entities = adsk.core.ObjectCollection.create()
                        for curve in selected_curves:
                            entities.add(curve)
                        transform = adsk.core.Matrix3D.create()
                        transform.translation = adsk.core.Vector3D.create(
                            float(op.get('dx', op.get('x', 0))),
                            float(op.get('dy', op.get('y', 0))),
                            0
                        )
                        s.move(entities, transform)
                        results.append(f"{action}:OK")
                elif action == 'copy_entities':
                    selected_curves, curve_err = get_selected_curves(op)
                    if curve_err:
                        results.append(f"{action}:{curve_err}")
                    else:
                        entities = adsk.core.ObjectCollection.create()
                        for curve in selected_curves:
                            entities.add(curve)
                        transform = adsk.core.Matrix3D.create()
                        transform.translation = adsk.core.Vector3D.create(
                            float(op.get('dx', op.get('x', 0))),
                            float(op.get('dy', op.get('y', 0))),
                            0
                        )
                        s.copy(entities, transform)
                        results.append(f"{action}:OK")
                elif action == 'mirror_entities':
                    selected_curves, curve_err = get_selected_curves(op)
                    if curve_err:
                        results.append(f"{action}:{curve_err}")
                    else:
                        axis_curve, axis_err = get_mirror_axis(op)
                        if axis_err:
                            results.append(f"{action}:{axis_err}")
                        else:
                            start_pt = axis_curve.startSketchPoint.geometry
                            end_pt = axis_curve.endSketchPoint.geometry
                            axis_dx = end_pt.x - start_pt.x
                            axis_dy = end_pt.y - start_pt.y
                            axis_length = math.hypot(axis_dx, axis_dy)
                            if axis_length <= 1e-9:
                                results.append(f"{action}:ERR_MIRROR_AXIS_INVALID")
                            else:
                                ux = axis_dx / axis_length
                                uy = axis_dy / axis_length
                                r00 = (2.0 * ux * ux) - 1.0
                                r01 = 2.0 * ux * uy
                                r10 = 2.0 * ux * uy
                                r11 = (2.0 * uy * uy) - 1.0
                                tx = start_pt.x - ((r00 * start_pt.x) + (r01 * start_pt.y))
                                ty = start_pt.y - ((r10 * start_pt.x) + (r11 * start_pt.y))

                                entities = adsk.core.ObjectCollection.create()
                                for curve in selected_curves:
                                    entities.add(curve)

                                transform = adsk.core.Matrix3D.create()
                                transform.setCell(0, 0, r00)
                                transform.setCell(0, 1, r01)
                                transform.setCell(1, 0, r10)
                                transform.setCell(1, 1, r11)
                                transform.setCell(0, 3, tx)
                                transform.setCell(1, 3, ty)
                                s.copy(entities, transform)
                                results.append(f"{action}:OK")
                elif action == 'set_construction':
                    curve, curve_err = get_curve(op)
                    if curve_err:
                        results.append(f"{action}:{curve_err}")
                    else:
                        curve.isConstruction = bool(op.get('value', True))
                        results.append(f"{action}:OK")
                elif action == 'trim':
                    curve, curve_err = get_curve(op)
                    if curve_err:
                        results.append(f"{action}:{curve_err}")
                    else:
                        trim_point = adsk.core.Point3D.create(op['x'], op['y'], 0)
                        curve.trim(trim_point)
                        results.append(f"{action}:OK")
                elif action == 'clear_sketch':
                    for idx in range(s.sketchTexts.count - 1, -1, -1):
                        s.sketchTexts.item(idx).deleteMe()
                    for curve in reversed(editable_curves()):
                        curve.deleteMe()
                    results.append(f"{action}:OK")
                elif action == 'add_constraint':
                    constraints = s.geometricConstraints
                    constraint_type = str(op.get('type', '')).lower()
                    if constraint_type in ('horizontal', 'vertical'):
                        curve, curve_err = get_curve(op)
                        if curve_err:
                            results.append(f"{action}:{curve_err}")
                        elif 'SketchLine' not in getattr(curve, 'objectType', ''):
                            results.append(f"{action}:ERR_INVALID_ENTITY")
                        else:
                            if constraint_type == 'horizontal':
                                constraints.addHorizontal(curve)
                            else:
                                constraints.addVertical(curve)
                            results.append(f"{action}:OK")
                    elif constraint_type in ('parallel', 'perpendicular', 'collinear'):
                        curve_one, curve_two, curve_err = get_curve_pair(op)
                        if curve_err:
                            results.append(f"{action}:{curve_err}")
                        elif 'SketchLine' not in getattr(curve_one, 'objectType', '') or 'SketchLine' not in getattr(curve_two, 'objectType', ''):
                            results.append(f"{action}:ERR_INVALID_ENTITY")
                        else:
                            if constraint_type == 'parallel':
                                constraints.addParallel(curve_one, curve_two)
                            elif constraint_type == 'perpendicular':
                                constraints.addPerpendicular(curve_one, curve_two)
                            else:
                                constraints.addCollinear(curve_one, curve_two)
                            results.append(f"{action}:OK")
                    elif constraint_type == 'tangent':
                        curve_one, curve_two, curve_err = get_curve_pair(op)
                        if curve_err:
                            results.append(f"{action}:{curve_err}")
                        else:
                            constraints.addTangent(curve_one, curve_two)
                            results.append(f"{action}:OK")
                    elif constraint_type == 'concentric':
                        curve_one, curve_two, curve_err = get_curve_pair(op)
                        if curve_err:
                            results.append(f"{action}:{curve_err}")
                        else:
                            constraints.addConcentric(curve_one, curve_two)
                            results.append(f"{action}:OK")
                    else:
                        results.append(f"{action}:ERR_UNKNOWN_CONSTRAINT_TYPE")
                elif action == 'remove_constraint':
                    constraint, constraint_err = get_constraint(op)
                    if constraint_err:
                        results.append(f"{action}:{constraint_err}")
                    else:
                        if hasattr(constraint, 'isDeletable') and not constraint.isDeletable:
                            results.append(f"{action}:ERR_CONSTRAINT_NOT_DELETABLE")
                        else:
                            constraint.deleteMe()
                            results.append(f"{action}:OK")
                elif action == 'set_dimension':
                    dimension, dimension_err = get_dimension(op)
                    if dimension_err:
                        results.append(f"{action}:{dimension_err}")
                    else:
                        dimension.value = float(op['value'])
                        results.append(f"{action}:OK")
                elif action == 'delete_dimension':
                    dimension, dimension_err = get_dimension(op)
                    if dimension_err:
                        results.append(f"{action}:{dimension_err}")
                    else:
                        if hasattr(dimension, 'isDeletable') and not dimension.isDeletable:
                            results.append(f"{action}:ERR_DIMENSION_NOT_DELETABLE")
                        else:
                            dimension.deleteMe()
                            results.append(f"{action}:OK")
                elif action == 'add_dimension':
                    dims = s.sketchDimensions
                    dimension_type = str(op.get('type', '')).lower()
                    if dimension_type == 'distance':
                        curve_one, curve_two, curve_err = get_curve_pair(op)
                        if curve_err:
                            results.append(f"{action}:{curve_err}")
                        elif not hasattr(curve_one, 'startSketchPoint') or not hasattr(curve_two, 'startSketchPoint'):
                            results.append(f"{action}:ERR_INVALID_ENTITY")
                        else:
                            dims.addDistanceDimension(
                                curve_one.startSketchPoint,
                                curve_two.startSketchPoint,
                                get_dimension_orientation(op.get('orientation')),
                                get_text_point(op),
                                bool(op.get('is_driving', True)),
                            )
                            results.append(f"{action}:OK")
                    elif dimension_type == 'radial':
                        curve, curve_err = get_curve(op)
                        if curve_err:
                            results.append(f"{action}:{curve_err}")
                        else:
                            dims.addRadialDimension(curve, get_text_point(op), bool(op.get('is_driving', True)))
                            results.append(f"{action}:OK")
                    elif dimension_type == 'diameter':
                        curve, curve_err = get_curve(op)
                        if curve_err:
                            results.append(f"{action}:{curve_err}")
                        else:
                            dims.addDiameterDimension(curve, get_text_point(op), bool(op.get('is_driving', True)))
                            results.append(f"{action}:OK")
                    elif dimension_type == 'angular':
                        curve_one, curve_two, curve_err = get_curve_pair(op)
                        if curve_err:
                            results.append(f"{action}:{curve_err}")
                        elif 'SketchLine' not in getattr(curve_one, 'objectType', '') or 'SketchLine' not in getattr(curve_two, 'objectType', ''):
                            results.append(f"{action}:ERR_INVALID_ENTITY")
                        else:
                            dims.addAngularDimension(curve_one, curve_two, get_text_point(op), bool(op.get('is_driving', True)))
                            results.append(f"{action}:OK")
                    else:
                        results.append(f"{action}:ERR_UNKNOWN_DIMENSION_TYPE")
                else:
                    results.append(f"{action}:ERR_UNKNOWN_ACTION")
            except Exception as e:
                results.append(f"{action}:ERR:{str(e)}")
        returnValue.append(",".join(results) if results else "OK")
    else:
        returnValue.append("ERR_SKETCH_NOT_FOUND")
except Exception as e:
    returnValue.append(f"ERR_API:{str(e)}")
"""
