from core.bridge import execute_fusion_script, FusionBridgeError
from core.utils import format_response, register_tool

def create_bolt_logic(diameter_mm: float, length_cm: float, modeled: bool = True, lang: str = "en"):
    """Business logic for creating a standard ISO bolt."""
    script = """
try:
    radius_cm = (params['dia_mm'] / 10.0) / 2.0
    s = root.sketches.add(root.xYConstructionPlane)
    s.sketchCurves.sketchCircles.addByCenterRadius(adsk.core.Point3D.create(0, 0, 0), radius_cm)
    prof = s.profiles.item(0)
    ext = root.features.extrudeFeatures.addSimple(prof, adsk.core.ValueInput.createByReal(params['length']), 0)
    body = ext.bodies.item(0)
    threads = root.features.threadFeatures
    face = next((f for f in body.faces if f.geometry.surfaceType == adsk.core.SurfaceTypes.CylinderSurfaceType), None)
    if face:
        q = threads.threadDataQuery
        t_type = 'ISO Metric profile'
        dia_val = float(params['dia_mm'])
        all_sizes = q.allSizes(t_type)
        size = str(params['dia_mm'])
        if size not in all_sizes:
            size = "{:.1f}".format(dia_val)
            if size not in all_sizes: size = "{:.0f}.0".format(dia_val)
        desigs = q.allDesignations(t_type, size)
        if len(desigs) > 0:
            actual_desig = desigs[0]
            classes = q.allClasses(False, t_type, actual_desig)
            actual_class = classes[0] if len(classes) > 0 else ""
            t_info = adsk.fusion.ThreadInfo.create(False, False, t_type, actual_desig, actual_class, True)
            t_input = threads.createInput(face, t_info)
            t_input.isModeled = params['modeled']
            threads.add(t_input)
            returnValue.append(size)
        else: returnValue.append("ERR_NO_THREAD")
    else: returnValue.append("ERR_NO_FACE")
except Exception as e:
    returnValue.append(f"ERR_API:{str(e)}")
"""
    try:
        res = execute_fusion_script(script, {"dia_mm": diameter_mm, "length": length_cm, "modeled": modeled})
        val = res.get("data", ["ERR_UNKNOWN"])[0]
        if val == "ERR_NO_THREAD": return format_response(lang, "no_thread_found", diameter=diameter_mm)
        if val == "ERR_NO_FACE": return format_response(lang, "face_not_found")
        if val.startswith("ERR_"): return format_response(lang, "unknown_error")
        return format_response(lang, "bolt_created", designation=f"M{val}")
    except FusionBridgeError as e: return f"Error: {str(e)}"

def register_mechanical_tools(mcp):
    register_tool(mcp, "create_bolt", create_bolt_logic)
