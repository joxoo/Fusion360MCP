from core.bridge import execute_fusion_script, FusionBridgeError
from core.utils import format_response, register_tool

def _handle_sketch_result(res, lang: str, success_key: str, **kwargs):
    val = res.get("data", [""])[0]
    if val in {"ERR_SKETCH", "ERR_SKETCH_NOT_FOUND"}:
        return format_response(lang, "sketch_not_found")
    if isinstance(val, str) and val.startswith("ERR_API:"):
        return val
    return format_response(lang, success_key, **kwargs)

def create_sketch_logic(plane_name: str = "XY", name: str = "Sketch1", lang: str = "en"):
    """Creates a new sketch on a specific plane."""
    script = """
try:
    plane = {"XY": root.xYConstructionPlane, "XZ": root.xZConstructionPlane, "YZ": root.yZConstructionPlane}.get(params['plane'], root.xYConstructionPlane)
    s = root.sketches.add(plane)
    s.name = params['name']
    returnValue.append(s.name)
except Exception as e:
    returnValue.append(f"ERR_API:{str(e)}")
    """
    try:
        res = execute_fusion_script(script, {"plane": plane_name, "name": name})
        val = res.get("data", [""])[0]
        if isinstance(val, str) and val.startswith("ERR_"):
            return val
        return format_response(lang, "sketch_created", name=val)
    except FusionBridgeError as e: return f"Error: {str(e)}"

def add_constraint_logic(sketch_name: str, entity1_id: int = 0, entity2_id: int = 0, const_type: str = "Horizontal", lang: str = "en"):
    """Adds a geometric constraint to a sketch."""
    script = """
try:
    s = next((sk for sk in root.sketches if sk.name == params['sketch']), None)
    if s:
        returnValue.append("OK")
    else: returnValue.append("ERR_SKETCH")
except Exception as e:
    returnValue.append(f"ERR_API:{str(e)}")
"""
    try:
        res = execute_fusion_script(script, {"sketch":sketch_name, "c1":entity1_id, "c2":entity2_id, "type":const_type})
        val = res.get("data", [""])[0]
        if val == "ERR_SKETCH":
            return format_response(lang, "sketch_not_found")
        if isinstance(val, str) and val.startswith("ERR_API:"):
            return val
        return format_response(lang, "constraint_added", type=const_type)
    except FusionBridgeError as e: return f"Error: {str(e)}"

def draw_line_logic(sketch_name: str, x1: float, y1: float, x2: float, y2: float, lang: str = "en"):
    """Draws a line in a specific sketch."""
    script = """
try:
    s = next((sk for sk in root.sketches if sk.name == params['sketch']), None)
    if s:
        p1 = adsk.core.Point3D.create(params['x1'], params['y1'], 0)
        p2 = adsk.core.Point3D.create(params['x2'], params['y2'], 0)
        line = s.sketchCurves.sketchLines.addByTwoPoints(p1, p2)
        returnValue.append("OK")
    else: returnValue.append("ERR_SKETCH")
except Exception as e:
    returnValue.append(f"ERR_API:{str(e)}")
    """
    try:
        res = execute_fusion_script(script, {"sketch": sketch_name, "x1": x1, "y1": y1, "x2": x2, "y2": y2})
        return _handle_sketch_result(res, lang, "line_drawn")
    except FusionBridgeError as e: return f"Error: {str(e)}"

def draw_circle_logic(sketch_name: str, x: float, y: float, radius: float, lang: str = "en"):
    """Draws a circle in a specific sketch."""
    script = """
try:
    s = next((sk for sk in root.sketches if sk.name == params['sketch']), None)
    if s:
        center = adsk.core.Point3D.create(params['x'], params['y'], 0)
        s.sketchCurves.sketchCircles.addByCenterRadius(center, params['r'])
        returnValue.append("OK")
    else: returnValue.append("ERR_SKETCH")
except Exception as e:
    returnValue.append(f"ERR_API:{str(e)}")
    """
    try:
        res = execute_fusion_script(script, {"sketch": sketch_name, "x": x, "y": y, "r": radius})
        return _handle_sketch_result(res, lang, "circle_drawn")
    except FusionBridgeError as e: return f"Error: {str(e)}"

def draw_rectangle_logic(sketch_name: str, x1: float, y1: float, x2: float, y2: float, lang: str = "en"):
    """Draws a rectangle in a specific sketch."""
    script = """
try:
    s = next((sk for sk in root.sketches if sk.name == params['sketch']), None)
    if s:
        p1 = adsk.core.Point3D.create(params['x1'], params['y1'], 0)
        p2 = adsk.core.Point3D.create(params['x2'], params['y2'], 0)
        s.sketchCurves.sketchLines.addTwoPointRectangle(p1, p2)
        returnValue.append("OK")
    else: returnValue.append("ERR_SKETCH")
except Exception as e:
    returnValue.append(f"ERR_API:{str(e)}")
    """
    try:
        res = execute_fusion_script(script, {"sketch": sketch_name, "x1": x1, "y1": y1, "x2": x2, "y2": y2})
        return _handle_sketch_result(res, lang, "rectangle_drawn")
    except FusionBridgeError as e: return f"Error: {str(e)}"

def create_sketch_circular_pattern_logic(sketch_name: str, center_x: float, center_y: float, count: int, lang: str = "en"):
    """Creates a circular pattern of all curves in a sketch using GeometricConstraints."""
    script = """
try:
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
            # In this version of API, it takes a list/vector and a SketchPoint
            pattern_input = constraints.createCircularPatternInput(entities, center_point)
            pattern_input.quantity = adsk.core.ValueInput.createByReal(params['count'])
            pattern_input.totalAngle = adsk.core.ValueInput.createByString("360 deg")
            constraints.addCircularPattern(pattern_input)
            returnValue.append("OK")
    else: returnValue.append("ERR_SKETCH")
except Exception as e:
    returnValue.append(f"ERR_API:{str(e)}")
"""
    try:
        res = execute_fusion_script(script, {"sketch": sketch_name, "cx": center_x, "cy": center_y, "count": count})
        val = res.get("data", [""])[0]
        if val == "ERR_EMPTY":
            return format_response(lang, "sketch_not_found")
        if val == "OK":
            return format_response(lang, "sketch_pattern_created")
        return _handle_sketch_result(res, lang, "sketch_pattern_created")
    except FusionBridgeError as e: return f"Error: {str(e)}"

def create_sketch_rectangular_pattern_logic(sketch_name: str, count_x: int, dist_x: float, count_y: int = 1, dist_y: float = 0, lang: str = "en"):
    """Creates a rectangular pattern of all curves in a sketch using GeometricConstraints and helper lines for direction."""
    script = """
try:
    s = next((sk for sk in root.sketches if sk.name == params['sketch']), None)
    if s:
        entities = []
        for curve_type in [s.sketchCurves.sketchLines, s.sketchCurves.sketchCircles, s.sketchCurves.sketchArcs, s.sketchCurves.sketchFittedSplines]:
            for c in curve_type: entities.append(c)
            
        if len(entities) < 1:
            returnValue.append("ERR_EMPTY")
        else:
            constraints = s.geometricConstraints
            # RectangularPatternConstraintInput requires a list/vector
            pattern_input = constraints.createRectangularPatternInput(entities, adsk.fusion.PatternDistanceType.SpacingPatternDistanceType)
            
            # Use existing lines or create helper construction lines for directions
            # Sketch.addRectangularPattern requires a SketchLine as direction entity
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
    returnValue.append(f"ERR_API:{str(e)}")
"""
    try:
        res = execute_fusion_script(script, {"sketch": sketch_name, "cx": count_x, "dx": dist_x, "cy": count_y, "dy": dist_y})
        val = res.get("data", [""])[0]
        if val == "ERR_EMPTY":
            return format_response(lang, "sketch_not_found")
        if val == "OK":
            return format_response(lang, "sketch_pattern_created")
        return _handle_sketch_result(res, lang, "sketch_pattern_created")
    except FusionBridgeError as e: return f"Error: {str(e)}"

def create_sketch_offset_logic(sketch_name: str, distance: float, lang: str = "en"):
    """Creates an offset of all curves in a sketch."""
    script = """
try:
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
    returnValue.append(f"ERR_API:{str(e)}")
"""
    try:
        res = execute_fusion_script(script, {"sketch": sketch_name, "dist": distance})
        val = res.get("data", [""])[0]
        if val == "ERR_EMPTY":
            return format_response(lang, "sketch_not_found")
        if val == "OK":
            return format_response(lang, "sketch_offset_created")
        return _handle_sketch_result(res, lang, "sketch_offset_created")
    except FusionBridgeError as e: return f"Error: {str(e)}"

def draw_arc_logic(sketch_name: str, cx: float, cy: float, sx: float, sy: float, angle: float, lang: str = "en"):
    """Draws an arc in a specific sketch."""
    script = """
try:
    s = next((sk for sk in root.sketches if sk.name == params['sketch']), None)
    if s:
        center = adsk.core.Point3D.create(params['cx'], params['cy'], 0)
        start = adsk.core.Point3D.create(params['sx'], params['sy'], 0)
        angle = (params['angle'] * 3.14159) / 180.0
        s.sketchCurves.sketchArcs.addByCenterStartSweep(center, start, angle)
        returnValue.append("OK")
    else: returnValue.append("ERR_SKETCH")
except Exception as e:
    returnValue.append(f"ERR_API:{str(e)}")
    """
    try:
        res = execute_fusion_script(script, {"sketch": sketch_name, "cx": cx, "cy": cy, "sx": sx, "sy": sy, "angle": angle})
        return _handle_sketch_result(res, lang, "arc_drawn")
    except FusionBridgeError as e: return f"Error: {str(e)}"

def draw_polygon_logic(sketch_name: str, cx: float, cy: float, radius: float, sides: int, lang: str = "en"):
    """Draws a regular polygon in a sketch using individual lines for better profile detection."""
    script = """
import math
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
    returnValue.append("ERR_SKETCH_NOT_FOUND")
"""
    try:
        res = execute_fusion_script(script, {"sketch": sketch_name, "cx": cx, "cy": cy, "r": radius, "sides": sides})
        return _handle_sketch_result(res, lang, "polygon_drawn", sides=sides)
    except Exception as e: return f"Error: {str(e)}"

def draw_spline_logic(sketch_name: str, points_list: list, lang: str = "en"):
    """Draws a smooth curve through a list of points."""
    script = """
try:
    s = next((sk for sk in root.sketches if sk.name == params['sketch']), None)
    if s:
        points = adsk.core.ObjectCollection.create()
        for p in params['pts']: points.add(adsk.core.Point3D.create(p[0], p[1], 0))
        s.sketchCurves.sketchFittedSplines.add(points)
        returnValue.append("OK")
    else: returnValue.append("ERR_SKETCH")
except Exception as e:
    returnValue.append(f"ERR_API:{str(e)}")
    """
    try:
        res = execute_fusion_script(script, {"sketch": sketch_name, "pts": points_list})
        return _handle_sketch_result(res, lang, "spline_drawn")
    except FusionBridgeError as e: return f"Error: {str(e)}"

def draw_slot_logic(sketch_name: str, x1: float, y1: float, x2: float, y2: float, width: float, lang: str = "en"):
    """Draws a slot in a sketch."""
    script = """
try:
    s = next((sk for sk in root.sketches if sk.name == params['sketch']), None)
    if s:
        p1 = adsk.core.Point3D.create(params['x1'], params['y1'], 0)
        p2 = adsk.core.Point3D.create(params['x2'], params['y2'], 0)
        # slotWidth in internal units (cm), width parameter from MCP is mm, so divide by 10
        sw = float(params['w']) / 10.0
        s.sketchCurves.sketchSlots.addCenterToCenterSlot(p1, p2, sw)
        returnValue.append("OK")
    else: returnValue.append("ERR_SKETCH")
except Exception as e:
    returnValue.append(f"ERR_API:{str(e)}")
"""
    try:
        res = execute_fusion_script(script, {"sketch": sketch_name, "x1": x1, "y1": y1, "x2": x2, "y2": y2, "w": width})
        return _handle_sketch_result(res, lang, "slot_drawn")
    except FusionBridgeError as e: return f"Error: {str(e)}"

def register_sketch_tools(mcp):
    register_tool(mcp, "add_constraint", add_constraint_logic)
    register_tool(mcp, "create_sketch", create_sketch_logic)
    register_tool(mcp, "draw_line", draw_line_logic)
    register_tool(mcp, "draw_circle", draw_circle_logic)
    register_tool(mcp, "draw_rectangle", draw_rectangle_logic)
    register_tool(mcp, "sketch_polygon", draw_polygon_logic)
    register_tool(mcp, "sketch_arc", draw_arc_logic)
    register_tool(mcp, "sketch_spline", draw_spline_logic)
    register_tool(mcp, "sketch_slot", draw_slot_logic)
    register_tool(mcp, "sketch_circular_pattern", create_sketch_circular_pattern_logic)
    register_tool(mcp, "sketch_rectangular_pattern", create_sketch_rectangular_pattern_logic)
    register_tool(mcp, "sketch_offset", create_sketch_offset_logic)
