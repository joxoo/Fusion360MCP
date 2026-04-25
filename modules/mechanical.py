from core.bridge import execute_fusion_script, get_i18n_data, FusionBridgeError
from core.utils import get_tool_definition, format_response
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
I18N = get_i18n_data(os.path.join(BASE_DIR, "i18n.json"))

def create_bolt_logic(diameter_mm: float, length_cm: float, modeled: bool, lang: str):
    """Business logic for creating a standard ISO bolt using numeric size resolution."""
    script = """
try:
    # 1. Profile
    radius_cm = (params['dia_mm'] / 10.0) / 2.0
    s = root.sketches.add(root.xYConstructionPlane)
    s.sketchCurves.sketchCircles.addByCenterRadius(adsk.core.Point3D.create(0, 0, 0), radius_cm)
    prof = s.profiles.item(0)
    
    # 2. Extrude
    ext = root.features.extrudeFeatures.addSimple(prof, adsk.core.ValueInput.createByReal(params['length']), 0)
    body = ext.bodies.item(0)
    
    # 3. Threading
    threads = root.features.threadFeatures
    face = next((f for f in body.faces if f.geometry.surfaceType == adsk.core.SurfaceTypes.CylinderSurfaceType), None)
            
    if face:
        q = threads.threadDataQuery
        t_type = 'ISO Metric profile'
        
        # Finding 1: Robust size resolution (tries numeric format if raw input fails)
        dia_val = float(params['dia_mm'])
        all_sizes = q.allSizes(t_type)
        size = str(params['dia_mm'])
        if size not in all_sizes:
            size = "{:.1f}".format(dia_val)
            if size not in all_sizes:
                size = "{:.0f}.0".format(dia_val) # Some versions prefer this
        
        desigs = q.allDesignations(t_type, size)
        
        if len(desigs) > 0:
            actual_desig = desigs[0]
            classes = q.allClasses(False, t_type, actual_desig)
            actual_class = classes[0] if len(classes) > 0 else ""
            
            # Finding 4: Detect internal/external based on normal
            # If normal points towards axis, it's internal
            (res, sp) = face.evaluator.getPointAtParameter(adsk.core.Point2D.create(0.5, 0.5))
            (res, normal) = face.evaluator.getNormalAtPoint(sp)
            axis_pt = face.geometry.origin
            vec_to_axis = axis_pt.asVector()
            vec_to_axis.subtract(sp.asVector())
            is_internal = normal.dotProduct(vec_to_axis) > 0
            
            # Using ThreadInfo.create with detected is_internal
            t_info = adsk.fusion.ThreadInfo.create(False, is_internal, t_type, actual_desig, actual_class, True)
            t_input = threads.createInput(face, t_info)
            t_input.isModeled = params['modeled']
            threads.add(t_input)
            returnValue.append(size)
        else:
            returnValue.append("ERR_NO_THREAD")
    else:
        returnValue.append("ERR_NO_FACE")
except Exception as e:
    returnValue.append(f"ERR_API:{str(e)}")
"""
    try:
        res = execute_fusion_script(script, {"dia_mm": diameter_mm, "length": length_cm, "modeled": modeled})
        val = res.get("data", ["ERR_UNKNOWN"])[0]
        
        if val.startswith("ERR_"):
            err_map = {
                "ERR_NO_THREAD": (f"Kein metrisches Gewinde für {diameter_mm}mm gefunden.", f"No metric thread found for {diameter_mm}mm."),
                "ERR_NO_FACE": ("Zylinderfläche nicht gefunden.", "Cylinder face not found."),
                "ERR_UNKNOWN": ("Unbekannter Fehler.", "Unknown error.")
            }
            msg = err_map.get(val, (val, val))
            return format_response(lang, msg[0], msg[1])
            
        return format_response(lang, f"Bolzen M{val} erstellt.", f"Bolt M{val} created.")
    except FusionBridgeError as e: return f"Error: {str(e)}"

def register_mechanical_tools(mcp):
    de_def, en_def = get_tool_definition(I18N, "create_bolt")
    if de_def: mcp.tool(name=de_def["name"], description=de_def["description"])(lambda diameter_mm, length_cm, modeled=True: create_bolt_logic(diameter_mm, length_cm, modeled, "de"))
    if en_def: mcp.tool(name=en_def["name"], description=en_def["description"])(lambda diameter_mm, length_cm, modeled=True: create_bolt_logic(diameter_mm, length_cm, modeled, "en"))
