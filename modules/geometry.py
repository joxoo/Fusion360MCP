from core.bridge import execute_fusion_script, FusionBridgeError
from core.utils import format_response, register_tool

def create_chamfer_logic(body: str, distance: float, lang: str = "en"):
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
        if res.get("data", [""])[0] == "ERROR": return format_response(lang, "body_not_found")
        return format_response(lang, "chamfer_created")
    except FusionBridgeError as e: return f"Error: {str(e)}"

def create_shell_logic(body: str, thickness: float, lang: str = "en"):
    """Hollows out a body with a given wall thickness."""
    script = """
try:
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
    returnValue.append(f"ERR_API:{str(e)}")
"""
    try:
        res = execute_fusion_script(script, {"body":body, "thick":thickness}, use_common=["find_body"])
        if res.get("data", [""])[0] == "ERROR": return format_response(lang, "body_not_found")
        return format_response(lang, "shell_created")
    except FusionBridgeError as e: return f"Error: {str(e)}"

def mirror_body_logic(body: str, plane_name: str, lang: str = "en"):
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
        if res.get("data", [""])[0] == "ERROR": return format_response(lang, "body_not_found")
        return format_response(lang, "mirror_created")
    except FusionBridgeError as e: return f"Error: {str(e)}"

def create_box_logic(l: float, w: float, h: float, name: str, x: float = 0, y: float = 0, z: float = 0, op: str = "NewBody", taper: float = 0, lang: str = "en"):
    """Creates a basic box at specified coordinates."""
    script = """
try:
    sketch_plane = root.xYConstructionPlane
    if abs(params['z']) > 1e-9:
        planes = root.constructionPlanes
        plane_input = planes.createInput()
        plane_input.setByOffset(root.xYConstructionPlane, adsk.core.ValueInput.createByReal(params['z']))
        sketch_plane = planes.add(plane_input)
    pt = adsk.core.Point3D.create(params['x'], params['y'], 0)
    s = root.sketches.add(sketch_plane)
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
        body.name = params['name']
        returnValue.append(body.name)
except Exception as e:
    returnValue.append(f"ERR_API:{str(e)}")
"""
    try:
        res = execute_fusion_script(script, {"l":l, "w":w, "h":h, "name":name, "x":x, "y":y, "z":z})
        val = res.get("data", [""])[0]
        if val == "ERR_NO_PROFILE": return format_response(lang, "sketch_not_found")
        if val.startswith("ERR_"): return val
        return format_response(lang, "box_created", name=val)
    except FusionBridgeError as e: return f"Error: {str(e)}"

def create_circular_pattern_logic(body_name: str, count: int, axis: str = "Z", lang: str = "en"):
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
        res = execute_fusion_script(script, {"body": body_name, "count": count, "axis": axis}, use_common=["find_body"])
        val = res.get("data", [""])[0]
        if val == "ERR_BODY": return format_response(lang, "body_not_found")
        return format_response(lang, "pattern_created")
    except FusionBridgeError as e: return f"Error: {str(e)}"

def create_rectangular_pattern_logic(body_name: str, count_x: int, dist_x: float, count_y: int = 1, dist_y: float = 0, lang: str = "en"):
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
        if val == "ERR_BODY": return format_response(lang, "body_not_found")
        return format_response(lang, "pattern_created")
    except FusionBridgeError as e: return f"Error: {str(e)}"

def create_fillet_logic(body_name: str, radius: float, lang: str = "en"):
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
        if val == "ERR_BODY": return format_response(lang, "body_not_found")
        return format_response(lang, "fillet_created")
    except FusionBridgeError as e: return f"Error: {str(e)}"

def extrude_sketch_logic(sketch_name: str, distance: float, lang: str = "en"):
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
        if val == "ERR_SKETCH": return format_response(lang, "sketch_not_found")
        return format_response(lang, "extrusion_created", name=sketch_name)
    except FusionBridgeError as e: return f"Error: {str(e)}"

def create_hole_logic(diameter_mm: float, x: float = 0, y: float = 0, lang: str = "en"):
    """Creates a simple hole in the active design."""
    script = """
try:
    pt = adsk.core.Point3D.create(params['x'], params['y'], 0)
    holes = root.features.holeFeatures
    h_in = holes.createSimpleInput(adsk.core.ValueInput.createByReal(params['d'] / 10.0))
    h_in.setPositionByPoint(root.xYConstructionPlane, pt)
    # Use Negative direction as it often goes 'into' the body from the XY plane
    h_in.setAllExtent(adsk.fusion.ExtentDirections.NegativeExtentDirection)
    holes.add(h_in)
    returnValue.append("OK")
except Exception as e:
    returnValue.append(f"ERR_API:{str(e)}")
"""
    try:
        res = execute_fusion_script(script, {"d": diameter_mm, "x": x, "y": y})
        val = res.get("data", [""])[0]
        if val == "OK": return format_response(lang, "hole_created")
        return f"Error: {val}"
    except FusionBridgeError as e: return f"Error: {str(e)}"

def register_geometry_tools(mcp):
    register_tool(mcp, "create_box", create_box_logic)
    register_tool(mcp, "create_hole", create_hole_logic)
    register_tool(mcp, "extrude_sketch", extrude_sketch_logic)
    register_tool(mcp, "create_circular_pattern", create_circular_pattern_logic)
    register_tool(mcp, "create_rectangular_pattern", create_rectangular_pattern_logic)
    register_tool(mcp, "create_chamfer", create_chamfer_logic)
    register_tool(mcp, "create_shell", create_shell_logic)
    register_tool(mcp, "create_fillet", create_fillet_logic)
    register_tool(mcp, "mirror_body", mirror_body_logic)
