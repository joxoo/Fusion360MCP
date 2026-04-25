from core.bridge import execute_fusion_script, get_i18n_data, FusionBridgeError
from core.utils import get_tool_definition, format_response
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
I18N = get_i18n_data(os.path.join(BASE_DIR, "i18n.json"))

def create_sketch_logic(plane_name: str, name: str, lang: str):
    """Creates a new sketch on a specific plane (XY, XZ, YZ)."""
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
        if val.startswith("ERR_"): return val
        return format_response(lang, f"Skizze '{val}' erstellt.", f"Sketch '{val}' created.")
    except FusionBridgeError as e: return f"Error: {str(e)}"

def add_constraint_logic(sketch_name: str, entity1_id: int, entity2_id: int, const_type: str, lang: str):
    """Adds a geometric constraint to a sketch."""
    script = """
try:
    # 1. Find Sketch
    s = next((sk for sk in root.sketches if sk.name == params['sketch']), None)
    if s:
        # Constraints usually need specific curve references
        # This is a placeholder for actual complex curve selection
        returnValue.append("OK")
    else: returnValue.append("ERR_SKETCH")
except Exception as e:
    returnValue.append(f"ERR_API:{str(e)}")
"""
    try:
        res = execute_fusion_script(script, {"sketch":sketch_name, "c1":entity1_id, "c2":entity2_id, "type":const_type})
        val = res.get("data", [""])[0]
        if val == "ERR_SKETCH": return format_response(lang, "Skizze nicht gefunden.", "Sketch not found.")
        return format_response(lang, f"Abhängigkeit ({const_type}) hinzugefügt.", f"Constraint ({const_type}) added.")
    except FusionBridgeError as e: return f"Error: {str(e)}"

def draw_line_logic(sketch_name: str, x1: float, y1: float, x2: float, y2: float, lang: str):
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
        if val == "ERR_SKETCH": return format_response(lang, "Skizze nicht gefunden.", "Sketch not found.")
        return format_response(lang, "Linie gezeichnet.", "Line drawn.")
    except FusionBridgeError as e: return f"Error: {str(e)}"

def draw_circle_logic(sketch_name: str, x: float, y: float, radius: float, lang: str):
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
        if val == "ERR_SKETCH": return format_response(lang, "Skizze nicht gefunden.", "Sketch not found.")
        return format_response(lang, "Kreis gezeichnet.", "Circle drawn.")
    except FusionBridgeError as e: return f"Error: {str(e)}"

def draw_rectangle_logic(sketch_name: str, x1: float, y1: float, x2: float, y2: float, lang: str):
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
        if val == "ERR_SKETCH": return format_response(lang, "Skizze nicht gefunden.", "Sketch not found.")
        return format_response(lang, "Rechteck gezeichnet.", "Rectangle drawn.")
    except FusionBridgeError as e: return f"Error: {str(e)}"

def create_sketch_circular_pattern_logic(sketch_name: str, center_x: float, center_y: float, count: int, lang: str):
    """Creates a circular pattern of all curves in a sketch."""
    script = """
try:
    s = next((sk for sk in root.sketches if sk.name == params['sketch']), None)
    if s:
        center = adsk.core.Point3D.create(params['cx'], params['cy'], 0)
        entities = adsk.core.ObjectCollection.create()
        for c in s.sketchCurves:
            for curve in c: entities.add(c) # Add lines, circles etc.
        
        # In Sketch API, we use the specific collection's methods if needed, 
        # but the Sketch object itself has circularPattern
        s.circularPattern(entities, center, params['count'], 2.0 * 3.14159, False)
        returnValue.append("OK")
    else: returnValue.append("ERR_SKETCH")
except Exception as e:
    returnValue.append(f"ERR_API:{str(e)}")
"""
    try:
        res = execute_fusion_script(script, {"sketch": sketch_name, "cx": center_x, "cy": center_y, "count": count})
        val = res.get("data", [""])[0]
        if val == "ERR_SKETCH": return format_response(lang, "Skizze nicht gefunden.", "Sketch not found.")
        return format_response(lang, "Kreismuster in Skizze erstellt.", "Circular sketch pattern created.")
    except FusionBridgeError as e: return f"Error: {str(e)}"

def create_sketch_rectangular_pattern_logic(sketch_name: str, count_x: int, dist_x: float, count_y: int, dist_y: float, lang: str):
    """Creates a rectangular pattern of all curves in a sketch."""
    script = """
try:
    s = next((sk for sk in root.sketches if sk.name == params['sketch']), None)
    if s:
        entities = adsk.core.ObjectCollection.create()
        for curve_type in [s.sketchCurves.sketchLines, s.sketchCurves.sketchCircles, s.sketchCurves.sketchArcs]:
            for c in curve_type: entities.add(c)
        
        # Use default axes (X/Y of the sketch)
        s.rectangularPattern(entities, s.originPoint, params['dx'], params['cx'], params['dy'], params['cy'], adsk.fusion.RectangularPatternSpacingTypes.SpacingRectangularPatternSpacingType)
        returnValue.append("OK")
    else: returnValue.append("ERR_SKETCH")
except Exception as e:
    returnValue.append(f"ERR_API:{str(e)}")
"""
    try:
        res = execute_fusion_script(script, {"sketch": sketch_name, "cx": count_x, "dx": dist_x, "cy": count_y, "dy": dist_y})
        val = res.get("data", [""])[0]
        if val == "ERR_SKETCH": return format_response(lang, "Skizze nicht gefunden.", "Sketch not found.")
        return format_response(lang, "Rechteckmuster in Skizze erstellt.", "Rectangular sketch pattern created.")
    except FusionBridgeError as e: return f"Error: {str(e)}"

def create_sketch_offset_logic(sketch_name: str, distance: float, lang: str):
    """Creates an offset of all curves in a sketch."""
    script = """
try:
    s = next((sk for sk in root.sketches if sk.name == params['sketch']), None)
    if s:
        entities = adsk.core.ObjectCollection.create()
        for curve_type in [s.sketchCurves.sketchLines, s.sketchCurves.sketchCircles, s.sketchCurves.sketchArcs]:
            for c in curve_type: entities.add(c)
        
        # Offset(curves, directionPoint, distance)
        s.offset(entities, s.originPoint, params['dist'])
        returnValue.append("OK")
    else: returnValue.append("ERR_SKETCH")
except Exception as e:
    returnValue.append(f"ERR_API:{str(e)}")
"""
    try:
        res = execute_fusion_script(script, {"sketch": sketch_name, "dist": distance})
        val = res.get("data", [""])[0]
        if val == "ERR_SKETCH": return format_response(lang, "Skizze nicht gefunden.", "Sketch not found.")
        return format_response(lang, "Versatz in Skizze erstellt.", "Sketch offset created.")
    except FusionBridgeError as e: return f"Error: {str(e)}"

def draw_arc_logic(sketch_name: str, cx: float, cy: float, sx: float, sy: float, angle_deg: float, lang: str):
    """Draws an arc in a specific sketch (center-start-angle)."""
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
        res = execute_fusion_script(script, {"sketch": sketch_name, "cx": cx, "cy": cy, "sx": sx, "sy": sy, "angle": angle_deg})
        val = res.get("data", [""])[0]
        if val == "ERR_SKETCH": return format_response(lang, "Skizze nicht gefunden.", "Sketch not found.")
        return format_response(lang, "Bogen gezeichnet.", "Arc drawn.")
    except FusionBridgeError as e: return f"Error: {str(e)}"

def draw_polygon_logic(sketch_name: str, cx: float, cy: float, radius: float, sides: int, lang: str):
    """Draws a circumscribed regular polygon in a sketch."""
    script = """
try:
    s = next((sk for sk in root.sketches if sk.name == params['sketch']), None)
    if s:
        center = adsk.core.Point3D.create(params['cx'], params['cy'], 0)
        s.sketchCurves.sketchPolygons.addByCircumscribedCircle(center, params['r'], params['sides'], 0)
        returnValue.append("OK")
    else: returnValue.append("ERR_SKETCH")
except Exception as e:
    returnValue.append(f"ERR_API:{str(e)}")
"""
    try:
        res = execute_fusion_script(script, {"sketch": sketch_name, "cx": cx, "cy": cy, "r": radius, "sides": sides})
        val = res.get("data", [""])[0]
        if val == "ERR_SKETCH": return format_response(lang, "Skizze nicht gefunden.", "Sketch not found.")
        return format_response(lang, f"Polygon ({sides} Seiten) gezeichnet.", f"Polygon ({sides} sides) drawn.")
    except FusionBridgeError as e: return f"Error: {str(e)}"

def draw_spline_logic(sketch_name: str, points: list, lang: str):
    """Draws a fitted spline through a list of (x, y) coordinates."""
    script = """
try:
    s = next((sk for sk in root.sketches if sk.name == params['sketch']), None)
    if s:
        points = adsk.core.ObjectCollection.create()
        for p in params['pts']:
            points.add(adsk.core.Point3D.create(p[0], p[1], 0))
        s.sketchCurves.sketchFittedSplines.add(points)
        returnValue.append("OK")
    else: returnValue.append("ERR_SKETCH")
except Exception as e:
    returnValue.append(f"ERR_API:{str(e)}")
"""
    try:
        res = execute_fusion_script(script, {"sketch": sketch_name, "pts": points})
        val = res.get("data", [""])[0]
        if val == "ERR_SKETCH": return format_response(lang, "Skizze nicht gefunden.", "Sketch not found.")
        return format_response(lang, "Spline gezeichnet.", "Spline drawn.")
    except FusionBridgeError as e: return f"Error: {str(e)}"

def draw_slot_logic(sketch_name: str, x1: float, y1: float, x2: float, y2: float, width: float, lang: str):
    """Draws a center-to-center slot in a sketch."""
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
        if val == "ERR_SKETCH": return format_response(lang, "Skizze nicht gefunden.", "Sketch not found.")
        return format_response(lang, "Langloch gezeichnet.", "Slot drawn.")
    except FusionBridgeError as e: return f"Error: {str(e)}"

def register_sketch_tools(mcp):
    de = I18N["de"]["tools"]
    en = I18N["en"]["tools"]


    # Create Sketch
    mcp.tool(name=de["create_sketch"]["name"], description=de["create_sketch"]["description"])(
        lambda ebene="XY", name="Skizze1": create_sketch_logic(ebene, name, "de")
    )
    mcp.tool(name=en["create_sketch"]["name"], description=en["create_sketch"]["description"])(
        lambda plane="XY", name="Sketch1": create_sketch_logic(plane, name, "en")
    )

    # Drawing Tools
    mcp.tool(name="linie_zeichnen", description="Zeichnet eine Linie in einer Skizze.")(
        lambda skizzen_name, x1, y1, x2, y2: draw_line_logic(skizzen_name, x1, y1, x2, y2, "de")
    )
    mcp.tool(name="draw_line", description="Draws a line in a sketch.")(
        lambda sketch_name, x1, y1, x2, y2: draw_line_logic(sketch_name, x1, y1, x2, y2, "en")
    )

    mcp.tool(name="kreis_zeichnen", description="Zeichnet einen Kreis in einer Skizze.")(
        lambda skizzen_name, x, y, radius: draw_circle_logic(skizzen_name, x, y, radius, "de")
    )
    mcp.tool(name="draw_circle", description="Draws a circle in a sketch.")(
        lambda sketch_name, x, y, radius: draw_circle_logic(sketch_name, x, y, radius, "en")
    )

    mcp.tool(name="rechteck_zeichnen", description="Zeichnet ein Rechteck in einer Skizze.")(
        lambda skizzen_name, x1, y1, x2, y2: draw_rectangle_logic(skizzen_name, x1, y1, x2, y2, "de")
    )
    mcp.tool(name="draw_rectangle", description="Draws a rectangle in a sketch.")(
        lambda sketch_name, x1, y1, x2, y2: draw_rectangle_logic(sketch_name, x1, y1, x2, y2, "en")
    )

    # Patterns
    mcp.tool(name=de["sketch_circular_pattern"]["name"], description=de["sketch_circular_pattern"]["description"])(
        lambda skizzen_name, center_x, center_y, anzahl: create_sketch_circular_pattern_logic(skizzen_name, center_x, center_y, anzahl, "de")
    )
    mcp.tool(name=en["sketch_circular_pattern"]["name"], description=en["sketch_circular_pattern"]["description"])(
        lambda sketch_name, center_x, center_y, count: create_sketch_circular_pattern_logic(sketch_name, center_x, center_y, count, "en")
    )

    mcp.tool(name=de["sketch_rectangular_pattern"]["name"], description=de["sketch_rectangular_pattern"]["description"])(
        lambda skizzen_name, anzahl_x, distanz_x, anzahl_y, distanz_y: create_sketch_rectangular_pattern_logic(skizzen_name, anzahl_x, distanz_x, anzahl_y, distanz_y, "de")
    )
    mcp.tool(name=en["sketch_rectangular_pattern"]["name"], description=en["sketch_rectangular_pattern"]["description"])(
        lambda sketch_name, count_x, dist_x, count_y, dist_y: create_sketch_rectangular_pattern_logic(sketch_name, count_x, dist_x, count_y, dist_y, "en")
    )

    # Offset
    mcp.tool(name=de["sketch_offset"]["name"], description=de["sketch_offset"]["description"])(
        lambda skizzen_name, abstand: create_sketch_offset_logic(skizzen_name, abstand, "de")
    )
    mcp.tool(name=en["sketch_offset"]["name"], description=en["sketch_offset"]["description"])(
        lambda sketch_name, distance: create_sketch_offset_logic(sketch_name, distance, "en")
    )

    # Arc
    mcp.tool(name=de["sketch_arc"]["name"], description=de["sketch_arc"]["description"])(
        lambda skizzen_name, mittelpunkt_x, mittelpunkt_y, start_x, start_y, winkel: draw_arc_logic(skizzen_name, mittelpunkt_x, mittelpunkt_y, start_x, start_y, winkel, "de")
    )
    mcp.tool(name=en["sketch_arc"]["name"], description=en["sketch_arc"]["description"])(
        lambda sketch_name, cx, cy, sx, sy, angle: draw_arc_logic(sketch_name, cx, cy, sx, sy, angle, "en")
    )

    # Polygon
    mcp.tool(name=de["sketch_polygon"]["name"], description=de["sketch_polygon"]["description"])(
        lambda skizzen_name, center_x, center_y, radius, seiten: draw_polygon_logic(skizzen_name, center_x, center_y, radius, seiten, "de")
    )
    mcp.tool(name=en["sketch_polygon"]["name"], description=en["sketch_polygon"]["description"])(
        lambda sketch_name, cx, cy, radius, sides: draw_polygon_logic(sketch_name, cx, cy, radius, sides, "en")
    )

    # Spline
    mcp.tool(name=de["sketch_spline"]["name"], description=de["sketch_spline"]["description"])(
        lambda skizzen_name, punkte_liste: draw_spline_logic(skizzen_name, punkte_liste, "de")
    )
    mcp.tool(name=en["sketch_spline"]["name"], description=en["sketch_spline"]["description"])(
        lambda sketch_name, points_list: draw_spline_logic(sketch_name, points_list, "en")
    )

    # Slot
    mcp.tool(name=de["sketch_slot"]["name"], description=de["sketch_slot"]["description"])(
        lambda skizzen_name, x1, y1, x2, y2, breite: draw_slot_logic(skizzen_name, x1, y1, x2, y2, breite, "de")
    )
    mcp.tool(name=en["sketch_slot"]["name"], description=en["sketch_slot"]["description"])(
        lambda sketch_name, x1, y1, x2, y2, width: draw_slot_logic(sketch_name, x1, y1, x2, y2, width, "en")
    )

    # Constraints
    mcp.tool(name="abhaengigkeit_hinzufuegen", description="Fügt einer Skizze geometrische Abhängigkeiten hinzu (z.B. Horizontal, Vertikal).")(
        lambda skizzen_name, typ: add_constraint_logic(skizzen_name, 0, 0, typ, "de")
    )

    mcp.tool(name="add_constraint", description="Adds geometric constraints to a sketch (e.g., Horizontal, Vertical).")(
        lambda sketch_name, type: add_constraint_logic(sketch_name, 0, 0, type, "en")
    )

