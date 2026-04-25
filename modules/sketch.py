from core.bridge import execute_fusion_script, FusionBridgeError
from core.utils import format_response, register_tool, load_i18n

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
        if isinstance(val, str) and val.startswith("ERR_"): return val
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
        if val == "ERR_SKETCH": return format_response(lang, "sketch_not_found")
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
        val = res.get("data", [""])[0]
        if val == "ERR_SKETCH": return format_response(lang, "sketch_not_found")
        if isinstance(val, str) and val.startswith("ERR_API:"): return val
        return format_response(lang, "line_drawn")
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
        val = res.get("data", [""])[0]
        if val == "ERR_SKETCH": return format_response(lang, "sketch_not_found")
        if isinstance(val, str) and val.startswith("ERR_API:"): return val
        return format_response(lang, "circle_drawn")
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
        val = res.get("data", [""])[0]
        if val == "ERR_SKETCH": return format_response(lang, "sketch_not_found")
        if isinstance(val, str) and val.startswith("ERR_API:"): return val
        return format_response(lang, "rectangle_drawn")
    except FusionBridgeError as e: return f"Error: {str(e)}"

def create_sketch_circular_pattern_logic(sketch_name: str, center_x: float, center_y: float, count: int, lang: str = "en"):
    """Creates a circular pattern of all curves in a sketch."""
    script = """
try:
    s = next((sk for sk in root.sketches if sk.name == params['sketch']), None)
    if s:
        center = adsk.core.Point3D.create(params['cx'], params['cy'], 0)
        entities = adsk.core.ObjectCollection.create()
        for c in s.sketchCurves:
            for curve in c: entities.add(c)
        s.circularPattern(entities, center, params['count'], 2.0 * 3.14159, False)
        returnValue.append("OK")
    else: returnValue.append("ERR_SKETCH")
except Exception as e:
    returnValue.append(f"ERR_API:{str(e)}")
"""
    try:
        res = execute_fusion_script(script, {"sketch": sketch_name, "cx": center_x, "cy": center_y, "count": count})
        val = res.get("data", [""])[0]
        if val == "ERR_SKETCH": return format_response(lang, "sketch_not_found")
        if isinstance(val, str) and val.startswith("ERR_API:"): return val
        return format_response(lang, "sketch_pattern_created")
    except FusionBridgeError as e: return f"Error: {str(e)}"

def create_sketch_rectangular_pattern_logic(sketch_name: str, count_x: int, dist_x: float, count_y: int = 1, dist_y: float = 0, lang: str = "en"):
    """Creates a rectangular pattern of all curves in a sketch."""
    script = """
try:
    s = next((sk for sk in root.sketches if sk.name == params['sketch']), None)
    if s:
        entities = adsk.core.ObjectCollection.create()
        for curve_type in [s.sketchCurves.sketchLines, s.sketchCurves.sketchCircles, s.sketchCurves.sketchArcs]:
            for c in curve_type: entities.add(c)
        s.rectangularPattern(entities, s.originPoint, params['dx'], params['cx'], params['dy'], params['cy'], adsk.fusion.RectangularPatternSpacingTypes.SpacingRectangularPatternSpacingType)
        returnValue.append("OK")
    else: returnValue.append("ERR_SKETCH")
except Exception as e:
    returnValue.append(f"ERR_API:{str(e)}")
"""
    try:
        res = execute_fusion_script(script, {"sketch": sketch_name, "cx": count_x, "dx": dist_x, "cy": count_y, "dy": dist_y})
        val = res.get("data", [""])[0]
        if val == "ERR_SKETCH": return format_response(lang, "sketch_not_found")
        if isinstance(val, str) and val.startswith("ERR_API:"): return val
        return format_response(lang, "sketch_pattern_created")
    except FusionBridgeError as e: return f"Error: {str(e)}"

def create_sketch_offset_logic(sketch_name: str, distance: float, lang: str = "en"):
    """Creates an offset of all curves in a sketch."""
    script = """
try:
    s = next((sk for sk in root.sketches if sk.name == params['sketch']), None)
    if s:
        entities = adsk.core.ObjectCollection.create()
        for curve_type in [s.sketchCurves.sketchLines, s.sketchCurves.sketchCircles, s.sketchCurves.sketchArcs]:
            for c in curve_type: entities.add(c)
        s.offset(entities, s.originPoint, params['dist'])
        returnValue.append("OK")
    else: returnValue.append("ERR_SKETCH")
except Exception as e:
    returnValue.append(f"ERR_API:{str(e)}")
"""
    try:
        res = execute_fusion_script(script, {"sketch": sketch_name, "dist": distance})
        val = res.get("data", [""])[0]
        if val == "ERR_SKETCH": return format_response(lang, "sketch_not_found")
        if isinstance(val, str) and val.startswith("ERR_API:"): return val
        return format_response(lang, "sketch_offset_created")
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
        val = res.get("data", [""])[0]
        if val == "ERR_SKETCH": return format_response(lang, "sketch_not_found")
        if isinstance(val, str) and val.startswith("ERR_API:"): return val
        return format_response(lang, "arc_drawn")
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
        val = res.get("data", [""])[0]
        if val == "ERR_SKETCH_NOT_FOUND": return format_response(lang, "sketch_not_found")
        if isinstance(val, str) and val.startswith("ERR_API:"): return val
        return format_response(lang, "polygon_drawn", sides=sides)
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
        val = res.get("data", [""])[0]
        if val == "ERR_SKETCH": return format_response(lang, "sketch_not_found")
        if isinstance(val, str) and val.startswith("ERR_API:"): return val
        return format_response(lang, "spline_drawn")
    except FusionBridgeError as e: return f"Error: {str(e)}"

def draw_slot_logic(sketch_name: str, x1: float, y1: float, x2: float, y2: float, width: float, lang: str = "en"):
    """Draws a slot in a sketch."""
    script = """
try:
    s = next((sk for sk in root.sketches if sk.name == params['sketch']), None)
    if s:
        p1 = adsk.core.Point3D.create(params['x1'], params['y1'], 0)
        p2 = adsk.core.Point3D.create(params['x2'], params['y2'], 0)
        s.sketchCurves.sketchSlots.addByCenterToCenter(p1, p2, params['w'])
        returnValue.append("OK")
    else: returnValue.append("ERR_SKETCH")
except Exception as e:
    returnValue.append(f"ERR_API:{str(e)}")
"""
    try:
        res = execute_fusion_script(script, {"sketch": sketch_name, "x1": x1, "y1": y1, "x2": x2, "y2": y2, "w": width})
        val = res.get("data", [""])[0]
        if val == "ERR_SKETCH": return format_response(lang, "sketch_not_found")
        if isinstance(val, str) and val.startswith("ERR_API:"): return val
        return format_response(lang, "slot_drawn")
    except FusionBridgeError as e: return f"Error: {str(e)}"

def register_sketch_tools(mcp):
    i18n = load_i18n()
    register_tool(mcp, "add_constraint", add_constraint_logic)

    de_create_sketch = i18n.get("de", {}).get("tools", {}).get("create_sketch")
    en_create_sketch = i18n.get("en", {}).get("tools", {}).get("create_sketch")
    de_draw_line = i18n.get("de", {}).get("tools", {}).get("draw_line")
    en_draw_line = i18n.get("en", {}).get("tools", {}).get("draw_line")
    de_draw_circle = i18n.get("de", {}).get("tools", {}).get("draw_circle")
    en_draw_circle = i18n.get("en", {}).get("tools", {}).get("draw_circle")
    de_draw_rectangle = i18n.get("de", {}).get("tools", {}).get("draw_rectangle")
    en_draw_rectangle = i18n.get("en", {}).get("tools", {}).get("draw_rectangle")
    de_polygon = i18n.get("de", {}).get("tools", {}).get("sketch_polygon")
    en_polygon = i18n.get("en", {}).get("tools", {}).get("sketch_polygon")
    de_arc = i18n.get("de", {}).get("tools", {}).get("sketch_arc")
    en_arc = i18n.get("en", {}).get("tools", {}).get("sketch_arc")
    de_spline = i18n.get("de", {}).get("tools", {}).get("sketch_spline")
    en_spline = i18n.get("en", {}).get("tools", {}).get("sketch_spline")
    de_slot = i18n.get("de", {}).get("tools", {}).get("sketch_slot")
    en_slot = i18n.get("en", {}).get("tools", {}).get("sketch_slot")
    de_circular_pattern = i18n.get("de", {}).get("tools", {}).get("sketch_circular_pattern")
    en_circular_pattern = i18n.get("en", {}).get("tools", {}).get("sketch_circular_pattern")
    de_rectangular_pattern = i18n.get("de", {}).get("tools", {}).get("sketch_rectangular_pattern")
    en_rectangular_pattern = i18n.get("en", {}).get("tools", {}).get("sketch_rectangular_pattern")
    de_offset = i18n.get("de", {}).get("tools", {}).get("sketch_offset")
    en_offset = i18n.get("en", {}).get("tools", {}).get("sketch_offset")

    if de_create_sketch:
        @mcp.tool(name=de_create_sketch["name"], description=de_create_sketch["description"])
        def skizze_erstellen(name: str = "Sketch1", ebene: str = "XY"):
            return create_sketch_logic(ebene, name, "de")

    if en_create_sketch:
        @mcp.tool(name=en_create_sketch["name"], description=en_create_sketch["description"])
        def create_sketch(name: str = "Sketch1", plane: str = "XY"):
            return create_sketch_logic(plane, name, "en")

    if de_draw_line:
        @mcp.tool(name=de_draw_line["name"], description=de_draw_line["description"])
        def linie_zeichnen(skizzen_name: str, x1: float, y1: float, x2: float, y2: float):
            return draw_line_logic(skizzen_name, x1, y1, x2, y2, "de")

    if en_draw_line:
        @mcp.tool(name=en_draw_line["name"], description=en_draw_line["description"])
        def draw_line(sketch_name: str, x1: float, y1: float, x2: float, y2: float):
            return draw_line_logic(sketch_name, x1, y1, x2, y2, "en")

    if de_draw_circle:
        @mcp.tool(name=de_draw_circle["name"], description=de_draw_circle["description"])
        def kreis_zeichnen(skizzen_name: str, center_x: float, center_y: float, radius: float):
            return draw_circle_logic(skizzen_name, center_x, center_y, radius, "de")

    if en_draw_circle:
        @mcp.tool(name=en_draw_circle["name"], description=en_draw_circle["description"])
        def draw_circle(sketch_name: str, center_x: float, center_y: float, radius: float):
            return draw_circle_logic(sketch_name, center_x, center_y, radius, "en")

    if de_draw_rectangle:
        @mcp.tool(name=de_draw_rectangle["name"], description=de_draw_rectangle["description"])
        def rechteck_zeichnen(skizzen_name: str, x1: float, y1: float, x2: float, y2: float):
            return draw_rectangle_logic(skizzen_name, x1, y1, x2, y2, "de")

    if en_draw_rectangle:
        @mcp.tool(name=en_draw_rectangle["name"], description=en_draw_rectangle["description"])
        def draw_rectangle(sketch_name: str, x1: float, y1: float, x2: float, y2: float):
            return draw_rectangle_logic(sketch_name, x1, y1, x2, y2, "en")

    if de_polygon:
        @mcp.tool(name=de_polygon["name"], description=de_polygon["description"])
        def polygon_zeichnen(skizzen_name: str, center_x: float, center_y: float, radius: float, seiten: int):
            return draw_polygon_logic(skizzen_name, center_x, center_y, radius, seiten, "de")

    if en_polygon:
        @mcp.tool(name=en_polygon["name"], description=en_polygon["description"])
        def draw_polygon(sketch_name: str, center_x: float, center_y: float, radius: float, sides: int):
            return draw_polygon_logic(sketch_name, center_x, center_y, radius, sides, "en")

    if de_arc:
        @mcp.tool(name=de_arc["name"], description=de_arc["description"])
        def bogen_zeichnen(skizzen_name: str, mittelpunkt_x: float, mittelpunkt_y: float, start_x: float, start_y: float, winkel: float):
            return draw_arc_logic(skizzen_name, mittelpunkt_x, mittelpunkt_y, start_x, start_y, winkel, "de")

    if en_arc:
        @mcp.tool(name=en_arc["name"], description=en_arc["description"])
        def draw_arc(sketch_name: str, center_x: float, center_y: float, start_x: float, start_y: float, angle: float):
            return draw_arc_logic(sketch_name, center_x, center_y, start_x, start_y, angle, "en")

    if de_spline:
        @mcp.tool(name=de_spline["name"], description=de_spline["description"])
        def spline_zeichnen(skizzen_name: str, punkte_liste: list):
            return draw_spline_logic(skizzen_name, punkte_liste, "de")

    if en_spline:
        @mcp.tool(name=en_spline["name"], description=en_spline["description"])
        def draw_spline(sketch_name: str, points_list: list):
            return draw_spline_logic(sketch_name, points_list, "en")

    if de_slot:
        @mcp.tool(name=de_slot["name"], description=de_slot["description"])
        def langloch_zeichnen(skizzen_name: str, x1: float, y1: float, x2: float, y2: float, breite: float):
            return draw_slot_logic(skizzen_name, x1, y1, x2, y2, breite, "de")

    if en_slot:
        @mcp.tool(name=en_slot["name"], description=en_slot["description"])
        def draw_slot(sketch_name: str, x1: float, y1: float, x2: float, y2: float, width: float):
            return draw_slot_logic(sketch_name, x1, y1, x2, y2, width, "en")

    if de_circular_pattern:
        @mcp.tool(name=de_circular_pattern["name"], description=de_circular_pattern["description"])
        def skizze_kreismuster(skizzen_name: str, center_x: float, center_y: float, anzahl: int):
            return create_sketch_circular_pattern_logic(skizzen_name, center_x, center_y, anzahl, "de")

    if en_circular_pattern:
        @mcp.tool(name=en_circular_pattern["name"], description=en_circular_pattern["description"])
        def sketch_circular_pattern(sketch_name: str, center_x: float, center_y: float, count: int):
            return create_sketch_circular_pattern_logic(sketch_name, center_x, center_y, count, "en")

    if de_rectangular_pattern:
        @mcp.tool(name=de_rectangular_pattern["name"], description=de_rectangular_pattern["description"])
        def skizze_rechteckmuster(skizzen_name: str, anzahl_x: int, distanz_x: float, anzahl_y: int = 1, distanz_y: float = 0):
            return create_sketch_rectangular_pattern_logic(skizzen_name, anzahl_x, distanz_x, anzahl_y, distanz_y, "de")

    if en_rectangular_pattern:
        @mcp.tool(name=en_rectangular_pattern["name"], description=en_rectangular_pattern["description"])
        def sketch_rectangular_pattern(sketch_name: str, count_x: int, dist_x: float, count_y: int = 1, dist_y: float = 0):
            return create_sketch_rectangular_pattern_logic(sketch_name, count_x, dist_x, count_y, dist_y, "en")

    if de_offset:
        @mcp.tool(name=de_offset["name"], description=de_offset["description"])
        def skizze_versatz(skizzen_name: str, abstand: float):
            return create_sketch_offset_logic(skizzen_name, abstand, "de")

    if en_offset:
        @mcp.tool(name=en_offset["name"], description=en_offset["description"])
        def sketch_offset(sketch_name: str, distance: float):
            return create_sketch_offset_logic(sketch_name, distance, "en")
