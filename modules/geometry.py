from core.bridge import execute_fusion_script, get_i18n_data, FusionBridgeError
from core.utils import get_tool_definition, format_response
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
I18N = get_i18n_data(os.path.join(BASE_DIR, "i18n.json"))

def create_chamfer_logic(body: str, distance: float, lang: str):
    """Adds a chamfer to all edges of a body."""
    script = """
try:
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
    returnValue.append(f"ERR_API:{str(e)}")
"""
    try:
        res = execute_fusion_script(script, {"body":body, "dist":distance}, use_common=["find_body"])
        if res.get("data", [""])[0] == "ERROR": return format_response(lang, "Körper nicht gefunden.", "Body not found.")
        return format_response(lang, "Fase erstellt.", "Chamfer created.")
    except FusionBridgeError as e: return f"Error: {str(e)}"

def create_shell_logic(body: str, thickness: float, lang: str):
    """Hollows out a body with a given wall thickness."""
    script = """
try:
    target = find_body_recursive(root, params['body'])
    if target:
        # Find top face (heuristic)
        face = next((f for f in target.faces if f.geometry.surfaceType == adsk.core.SurfaceTypes.PlaneSurfaceType), target.faces.item(0))
        faces = adsk.core.ObjectCollection.create(); faces.add(face)
        shells = target.parentComponent.features.shellFeatures
        s_in = shells.createInput(faces, False)
        s_in.insideThickness = adsk.core.ValueInput.createByReal(params['thick'])
        shells.add(s_in)
        returnValue.append("OK")
    else: returnValue.append("ERROR")
except Exception as e:
    returnValue.append(f"ERR_API:{str(e)}")
"""
    try:
        res = execute_fusion_script(script, {"body":body, "thick":thickness}, use_common=["find_body"])
        if res.get("data", [""])[0] == "ERROR": return format_response(lang, "Körper nicht gefunden.", "Body not found.")
        return format_response(lang, "Schale erstellt.", "Shell created.")
    except FusionBridgeError as e: return f"Error: {str(e)}"

def mirror_entities_logic(body: str, plane_name: str, lang: str):
    """Mirrors a body across a construction plane."""
    script = """
try:
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
    returnValue.append(f"ERR_API:{str(e)}")
"""
    try:
        res = execute_fusion_script(script, {"body":body, "plane":plane_name}, use_common=["find_body"])
        if res.get("data", [""])[0] == "ERROR": return format_response(lang, "Körper nicht gefunden.", "Body not found.")
        return format_response(lang, "Spiegelung erstellt.", "Mirror created.")
    except FusionBridgeError as e: return f"Error: {str(e)}"

def create_box_logic(l: float, w: float, h: float, name: str, x: float, y: float, z: float, op: str, taper: float, lang: str):
    """Creates a basic box at specified coordinates."""
    script = """
try:
    pt = adsk.core.Point3D.create(params['x'], params['y'], params['z'])
    s = root.sketches.add(root.xYConstructionPlane)
    s.sketchCurves.sketchLines.addTwoPointRectangle(
        pt, adsk.core.Point3D.create(pt.x + params['l'], pt.y + params['w'], 0)
    )
    prof = s.profiles.item(0)
    box = root.features.extrudeFeatures.addSimple(
        prof,
        adsk.core.ValueInput.createByReal(params['h']),
        adsk.fusion.FeatureOperations.NewBodyFeatureOperation
    )
    body = box.bodies.item(0)
    body.name = params['name']
    returnValue.append(body.name)
except Exception as e:
    returnValue.append(f"ERR_API:{str(e)}")
"""
    try:
        res = execute_fusion_script(script, {"l":l, "w":w, "h":h, "name":name, "x":x, "y":y, "z":z})
        val = res.get("data", [""])[0]
        if val.startswith("ERR_"): return val
        return format_response(lang, f"Box '{val}' erstellt.", f"Box '{val}' created.")
    except FusionBridgeError as e: return f"Error: {str(e)}"

def create_circular_pattern_logic(body_name: str, count: int, axis_name: str, lang: str):
    """Creates a circular pattern of a body around an axis (X, Y, Z)."""
    script = """
try:
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
    returnValue.append(f"ERR_API:{str(e)}")
"""
    try:
        res = execute_fusion_script(script, {"body": body_name, "count": count, "axis": axis_name}, use_common=["find_body"])
        val = res.get("data", [""])[0]
        if val == "ERR_BODY": return format_response(lang, "Körper nicht gefunden.", "Body not found.")
        return format_response(lang, "Kreismuster erstellt.", "Circular pattern created.")
    except FusionBridgeError as e: return f"Error: {str(e)}"

def create_rectangular_pattern_logic(body_name: str, count_x: int, dist_x: float, count_y: int, dist_y: float, lang: str):
    """Creates a rectangular pattern of a body."""
    script = """
try:
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
    returnValue.append(f"ERR_API:{str(e)}")
"""
    try:
        res = execute_fusion_script(script, {"body": body_name, "cx": count_x, "dx": dist_x, "cy": count_y, "dy": dist_y}, use_common=["find_body"])
        val = res.get("data", [""])[0]
        if val == "ERR_BODY": return format_response(lang, "Körper nicht gefunden.", "Body not found.")
        return format_response(lang, "Rechteckmuster erstellt.", "Rectangular pattern created.")
    except FusionBridgeError as e: return f"Error: {str(e)}"

def create_fillet_logic(body_name: str, radius: float, lang: str):
    """Adds a fillet to all edges of a body."""
    script = """
try:
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
    returnValue.append(f"ERR_API:{str(e)}")
"""
    try:
        res = execute_fusion_script(script, {"body": body_name, "r": radius}, use_common=["find_body"])
        val = res.get("data", [""])[0]
        if val == "ERR_BODY": return format_response(lang, "Körper nicht gefunden.", "Body not found.")
        return format_response(lang, "Abrundung erstellt.", "Fillet created.")
    except FusionBridgeError as e: return f"Error: {str(e)}"

def extrude_sketch_logic(sketch_name: str, distance: float, lang: str):
    """Extrudes the first profile of a sketch."""
    script = """
try:
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
    returnValue.append(f"ERR_API:{str(e)}")
"""
    try:
        res = execute_fusion_script(script, {"sketch": sketch_name, "dist": distance})
        val = res.get("data", [""])[0]
        if val == "ERR_SKETCH": return format_response(lang, "Skizze oder Profil nicht gefunden.", "Sketch or profile not found.")
        return format_response(lang, f"Extrusion von '{sketch_name}' erstellt.", f"Extrusion of '{sketch_name}' created.")
    except FusionBridgeError as e: return f"Error: {str(e)}"

def register_geometry_tools(mcp):
    de = I18N["de"]["tools"]
    en = I18N["en"]["tools"]

    # Basic Box
    mcp.tool(name=de["create_box"]["name"], description=de["create_box"]["description"])(
        lambda laenge, breite, hoehe, name="Box", x=0, y=0, z=0, op="NewBody", taper=0: 
        create_box_logic(laenge, breite, hoehe, name, x, y, z, op, taper, "de")
    )
    mcp.tool(name=en["create_box"]["name"], description=en["create_box"]["description"])(
        lambda l, w, h, name="Box", x=0, y=0, z=0, op="NewBody", taper=0: 
        create_box_logic(l, w, h, name, x, y, z, op, taper, "en")
    )

    # Extrude
    mcp.tool(name="extrudieren", description="Extrudiert das erste Profil einer Skizze.")(
        lambda skizzen_name, distanz_cm: extrude_sketch_logic(skizzen_name, distanz_cm, "de")
    )
    mcp.tool(name="extrude_sketch", description="Extrudes the first profile of a sketch.")(
        lambda sketch_name, distance_cm: extrude_sketch_logic(sketch_name, distance_cm, "en")
    )

    # Patterns (Bodies)
    mcp.tool(name=de["kreismuster_erstellen"]["name"], description=de["kreismuster_erstellen"]["description"])(
        lambda koerper_name, anzahl, achse="Z": create_circular_pattern_logic(koerper_name, anzahl, achse, "de")
    )
    mcp.tool(name=en["kreismuster_erstellen"]["name"], description=en["kreismuster_erstellen"]["description"])(
        lambda body_name, count, axis="Z": create_circular_pattern_logic(body_name, count, axis, "en")
    )

    mcp.tool(name="rechteckmuster_erstellen")(
        lambda koerper_name, anzahl_x, distanz_x, anzahl_y=1, distanz_y=0: create_rectangular_pattern_logic(koerper_name, anzahl_x, distanz_x, anzahl_y, distanz_y, "de")
    )
    mcp.tool(name="create_rectangular_pattern")(
        lambda body_name, count_x, dist_x, count_y=1, dist_y=0: create_rectangular_pattern_logic(body_name, count_x, dist_x, count_y, dist_y, "en")
    )

    # Advanced Tools
    mcp.tool(name="fase_erstellen")(lambda koerper_name, abstand_cm: create_chamfer_logic(koerper_name, abstand_cm, "de"))
    mcp.tool(name="create_chamfer")(lambda body_name, distance_cm: create_chamfer_logic(body_name, distance_cm, "en"))

    mcp.tool(name="schale_erstellen")(lambda koerper_name, wandstaerke_cm: create_shell_logic(koerper_name, wandstaerke_cm, "de"))
    mcp.tool(name="create_shell")(lambda body_name, thickness_cm: create_shell_logic(body_name, thickness_cm, "en"))

    mcp.tool(name=de["abrunden_erstellen"]["name"], description=de["abrunden_erstellen"]["description"])(
        lambda koerper_name, radius_cm: create_fillet_logic(koerper_name, radius_cm, "de")
    )
    mcp.tool(name=en["abrunden_erstellen"]["name"], description=en["abrunden_erstellen"]["description"])(
        lambda body_name, radius_cm: create_fillet_logic(body_name, radius_cm, "en")
    )

    mcp.tool(name="spiegeln")(lambda koerper_name, ebene="XY": mirror_entities_logic(koerper_name, ebene, "de"))
    mcp.tool(name="mirror_body")(lambda body_name, plane="XY": mirror_entities_logic(body_name, plane, "en"))
