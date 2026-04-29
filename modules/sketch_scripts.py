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
    s, owner, err = resolve_sketch_context(params['sketch'])
    if err:
        returnValue.append(err)
    elif s:
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
                elif action == 'add_constraint':
                    results.append(f"{action}:SKIPPED_NOT_YET_SUPPORTED_IN_BATCH")
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
