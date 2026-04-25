from core.bridge import execute_fusion_script, get_i18n_data, FusionBridgeError
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
I18N_PATH = os.path.join(BASE_DIR, "i18n.json")
I18N = get_i18n_data(I18N_PATH)

def create_bolt_logic(diameter_mm: float, length_cm: float, lang: str, modeled: bool):
    script = """
import math
import traceback
try:
    d = adsk.fusion.Design.cast(app.activeProduct)
    c = d.rootComponent
    
    dia = params['dia_mm']
    l_cm = params['l_cm']
    is_modeled = params['modeled']
    radius_cm = (dia / 10.0) / 2.0

    # 1. Geometrie
    s = c.sketches.add(c.xYConstructionPlane)
    s.sketchCurves.sketchCircles.addByCenterRadius(adsk.core.Point3D.create(0,0,0), radius_cm)
    b = c.features.extrudeFeatures.addSimple(s.profiles.item(0), adsk.core.ValueInput.createByReal(l_cm), 0).bodies.item(0)

    # 2. Gewinde
    try:
        f = next(f for f in b.faces if f.geometry.objectType == adsk.core.Cylinder.classType())
        tf = c.features.threadFeatures
        q = adsk.fusion.ThreadDataQuery.create()
        
        t_type = q.defaultMetricThreadType
        success, designation, t_class = q.recommendThreadData(radius_cm * 2.0, False, t_type)
        
        if success:
            # Fix Finding 6: Dummy check entfernt
            t_info = adsk.fusion.ThreadInfo.create(False, False, t_type, designation, t_class, True)
            if not t_info:
                raise RuntimeError(f"ThreadInfo.create failed for {designation}.")
            
            t_input = tf.createInput(f, t_info)
            t_input.isModeled = is_modeled
            tf.add(t_input)
            returnValue.append(f"Erfolg: Bolt with {designation} ({t_class}) created.")
        else:
            returnValue.append(f"Error: No thread recommendation found for {dia}mm.")
    except Exception as e:
        returnValue.append(f"Geometry OK, Thread Error: {str(e)}")
except Exception as e:
    returnValue.append(f"Fatal Error: {str(e)}")
"""
    try:
        res = execute_fusion_script(script, {"dia_mm": diameter_mm, "l_cm": length_cm, "modeled": modeled})
        return res.get("data", ["Error"])[0]
    except FusionBridgeError as e:
        return str(e)

def register_mechanical_tools(mcp):
    # DEUTSCH
    de_b = I18N["de"]["tools"]["create_bolt"]
    @mcp.tool(name=de_b["name"], description=de_b["description"])
    def bolzen_erstellen(durchmesser_mm: float, laenge_cm: float, modelliert: bool = True) -> str:
        return create_bolt_logic(durchmesser_mm, laenge_cm, "de", modelliert)

    # ENGLISCH
    en_b = I18N["en"]["tools"]["create_bolt"]
    @mcp.tool(name=en_b["name"], description=en_b["description"])
    def create_bolt(diameter_mm: float, length_cm: float, modeled: bool = True) -> str:
        return create_bolt_logic(diameter_mm, length_cm, "en", modeled)
