def build_create_sketch_script() -> str:
    return """try:
    plane = {"XY": root.xYConstructionPlane, "XZ": root.xZConstructionPlane, "YZ": root.yZConstructionPlane}.get(params['plane'], root.xYConstructionPlane)
    s = root.sketches.add(plane)
    s.name = params['name']
    returnValue.append(s.name)
except Exception as e:
    returnValue.append(f"ERR_API:{str(e)}")"""


def build_add_constraint_script() -> str:
    return """try:
    s = next((sk for sk in root.sketches if sk.name == params['sketch']), None)
    if s:
        returnValue.append("OK")
    else: returnValue.append("ERR_SKETCH")
except Exception as e:
    returnValue.append(f"ERR_API:{str(e)}")"""


def build_draw_line_script() -> str:
    return """try:
    s = next((sk for sk in root.sketches if sk.name == params['sketch']), None)
    if s:
        p1 = adsk.core.Point3D.create(params['x1'], params['y1'], 0)
        p2 = adsk.core.Point3D.create(params['x2'], params['y2'], 0)
        line = s.sketchCurves.sketchLines.addByTwoPoints(p1, p2)
        returnValue.append("OK")
    else: returnValue.append("ERR_SKETCH")
except Exception as e:
    returnValue.append(f"ERR_API:{str(e)}")"""


def build_draw_circle_script() -> str:
    return """try:
    s = next((sk for sk in root.sketches if sk.name == params['sketch']), None)
    if s:
        center = adsk.core.Point3D.create(params['x'], params['y'], 0)
        s.sketchCurves.sketchCircles.addByCenterRadius(center, params['r'])
        returnValue.append("OK")
    else: returnValue.append("ERR_SKETCH")
except Exception as e:
    returnValue.append(f"ERR_API:{str(e)}")"""


def build_draw_rectangle_script() -> str:
    return """try:
    s = next((sk for sk in root.sketches if sk.name == params['sketch']), None)
    if s:
        p1 = adsk.core.Point3D.create(params['x1'], params['y1'], 0)
        p2 = adsk.core.Point3D.create(params['x2'], params['y2'], 0)
        s.sketchCurves.sketchLines.addTwoPointRectangle(p1, p2)
        returnValue.append("OK")
    else: returnValue.append("ERR_SKETCH")
except Exception as e:
    returnValue.append(f"ERR_API:{str(e)}")"""


def build_sketch_circular_pattern_script() -> str:
    return """try:
    s = next((sk for sk in root.sketches if sk.name == params['sketch']), None)
    if s:
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
    else: returnValue.append("ERR_SKETCH")
except Exception as e:
    returnValue.append(f"ERR_API:{str(e)}")"""


def build_sketch_rectangular_pattern_script() -> str:
    return """try:
    s = next((sk for sk in root.sketches if sk.name == params['sketch']), None)
    if s:
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
    else: returnValue.append("ERR_SKETCH")
except Exception as e:
    returnValue.append(f"ERR_API:{str(e)}")"""


def build_sketch_offset_script() -> str:
    return """try:
    s = next((sk for sk in root.sketches if sk.name == params['sketch']), None)
    if s:
        entities = adsk.core.ObjectCollection.create()
        for curve_type in [s.sketchCurves.sketchLines, s.sketchCurves.sketchCircles, s.sketchCurves.sketchArcs, s.sketchCurves.sketchFittedSplines]:
            for c in curve_type: entities.add(c)
        if entities.count < 1:
            returnValue.append("ERR_EMPTY")
        else:
            offset_point = adsk.core.Point3D.create(10.0, 10.0, 0)
            s.offset(entities, offset_point, params['dist'])
            returnValue.append("OK")
    else: returnValue.append("ERR_SKETCH")
except Exception as e:
    returnValue.append(f"ERR_API:{str(e)}")"""


def build_draw_arc_script() -> str:
    return """try:
    s = next((sk for sk in root.sketches if sk.name == params['sketch']), None)
    if s:
        center = adsk.core.Point3D.create(params['cx'], params['cy'], 0)
        start = adsk.core.Point3D.create(params['sx'], params['sy'], 0)
        angle = (params['angle'] * 3.14159) / 180.0
        s.sketchCurves.sketchArcs.addByCenterStartSweep(center, start, angle)
        returnValue.append("OK")
    else: returnValue.append("ERR_SKETCH")
except Exception as e:
    returnValue.append(f"ERR_API:{str(e)}")"""


def build_draw_polygon_script() -> str:
    return """import math
sketch_name = params.get('sketch')
s = next((sk for sk in root.sketches if sk.name == sketch_name), None)
if s:
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
    returnValue.append("ERR_SKETCH_NOT_FOUND")"""


def build_draw_spline_script() -> str:
    return """try:
    s = next((sk for sk in root.sketches if sk.name == params['sketch']), None)
    if s:
        points = adsk.core.ObjectCollection.create()
        for p in params['pts']: points.add(adsk.core.Point3D.create(p[0], p[1], 0))
        s.sketchCurves.sketchFittedSplines.add(points)
        returnValue.append("OK")
    else: returnValue.append("ERR_SKETCH")
except Exception as e:
    returnValue.append(f"ERR_API:{str(e)}")"""


def build_draw_slot_script() -> str:
    return """try:
    s = next((sk for sk in root.sketches if sk.name == params['sketch']), None)
    if s:
        p1 = adsk.core.Point3D.create(params['x1'], params['y1'], 0)
        p2 = adsk.core.Point3D.create(params['x2'], params['y2'], 0)
        sw = float(params['w']) / 10.0
        s.sketchCurves.sketchSlots.addCenterToCenterSlot(p1, p2, sw)
        returnValue.append("OK")
    else: returnValue.append("ERR_SKETCH")
except Exception as e:
    returnValue.append(f"ERR_API:{str(e)}")"""
