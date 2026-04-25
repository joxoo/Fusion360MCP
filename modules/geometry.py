from core.bridge import execute_fusion_script, get_i18n_data, FusionBridgeError
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
I18N_PATH = os.path.join(BASE_DIR, "i18n.json")
I18N = get_i18n_data(I18N_PATH)

def create_component_logic(name: str):
    script = "newOcc = app.activeProduct.rootComponent.occurrences.addNewComponent(adsk.core.Matrix3D.create()); newOcc.component.name = params['name']; returnValue.append('Created')"
    try:
        res = execute_fusion_script(script, {"name": name})
        return res.get("data", ["Error"])[0]
    except FusionBridgeError as e:
        return str(e)

def create_sketch_logic(plane: str, component_name: str):
    script = """
c = app.activeProduct.rootComponent
comp_name = params['component_name']
if comp_name != "Root":
    def find_comp_recursive(root_comp, target_name):
        for occ in root_comp.allOccurrences:
            if occ.component.name == target_name: return occ.component
            res = find_comp_recursive(occ.component, target_name)
            if res: return res
        return None
    found_c = find_comp_recursive(c, comp_name)
    if found_c: c = found_c

planes = {"XY": c.xYConstructionPlane, "YZ": c.yZConstructionPlane, "XZ": c.xZConstructionPlane}
s = c.sketches.add(planes.get(params['plane'], c.xYConstructionPlane))
returnValue.append(f"Sketch on {params['plane']} created in {c.name}.")
"""
    try:
        res = execute_fusion_script(script, {"plane": plane, "component_name": component_name})
        return res.get("data", ["Error"])[0]
    except FusionBridgeError as e:
        return str(e)

def create_box_logic(length_cm: float, width_cm: float, height_cm: float, name: str, x_cm: float = 0, y_cm: float = 0, z_cm: float = 0, operation: str = "NewBody"):
    script = """
import adsk.core, adsk.fusion
try:
    d = adsk.fusion.Design.cast(app.activeProduct)
    c = d.rootComponent
    feat_name = f"FEAT_Box_{params['name']}"
    
    # Operation Mapping
    ops = {
        "NewBody": adsk.fusion.FeatureOperations.NewBodyFeatureOperation,
        "Join": adsk.fusion.FeatureOperations.JoinFeatureOperation,
        "Cut": adsk.fusion.FeatureOperations.CutFeatureOperation
    }
    op = ops.get(params.get('op', 'NewBody'), adsk.fusion.FeatureOperations.NewBodyFeatureOperation)

    # Suchen ob Feature bereits existiert (Bearbeitungs-Modus)
    existing_feat = c.features.extrudeFeatures.itemByName(feat_name)
    
    if existing_feat:
        # 1. Hoehe anpassen
        existing_feat.extentDefinition.distance.value = params['h']
        returnValue.append(f"Box-Feature '{feat_name}' wurde auf Hoehe {params['h']}cm aktualisiert.")
    else:
        # Neu erstellen
        s = c.sketches.add(c.xYConstructionPlane)
        lines = s.sketchCurves.sketchLines
        l, w, h = params['l'], params['w'], params['h']
        x, y, z = params.get('x', 0), params.get('y', 0), params.get('z', 0)
        
        lines.addTwoPointRectangle(adsk.core.Point3D.create(x, y, z), adsk.core.Point3D.create(x + l, y + w, z))
        prof = s.profiles.item(0)
        ext = c.features.extrudeFeatures.addSimple(prof, adsk.core.ValueInput.createByReal(h), op)
        ext.name = feat_name
        if op == adsk.fusion.FeatureOperations.NewBodyFeatureOperation:
            ext.bodies.item(0).name = params['name']
        returnValue.append(f"Box {params['name']} ({l}x{w}x{h}) bei ({x},{y},{z}) mit Operation {params.get('op', 'NewBody')} neu erstellt.")
except Exception as e:
    returnValue.append(f"Error: {str(e)}")
"""
    try:
        res = execute_fusion_script(script, {"l": length_cm, "w": width_cm, "h": height_cm, "name": name, "x": x_cm, "y": y_cm, "z": z_cm, "op": operation})
        return res.get("data", ["Error"])[0]
    except FusionBridgeError as e:
        return str(e)

def create_hole_logic(diameter_mm: float, depth_cm: float, body_name: str, x_cm: float = None, y_cm: float = None):
    script = """
import adsk.core, adsk.fusion
try:
    d = adsk.fusion.Design.cast(app.activeProduct)
    root = d.rootComponent
    
    def find_body_recursive(component, target_name):
        for b in component.bRepBodies:
            if b.name == target_name or not target_name: return b
        for occ in component.occurrences:
            res = find_body_recursive(occ.component, target_name)
            if res: return res
        return None

    body = find_body_recursive(root, params['body_name'])
    if not body:
        returnValue.append("Error: Body not found.")
    else:
        comp = body.parentComponent
        feat_name = f"FEAT_Hole_{body.name}_{params['dia_mm']}"
        
        existing_feat = comp.features.extrudeFeatures.itemByName(feat_name)
        
        if existing_feat:
            # Bestehendes Feature bearbeiten
            dist = params['depth']
            if dist <= 0: dist = body.boundingBox.maxPoint.z - body.boundingBox.minPoint.z + 0.1
            existing_feat.extentDefinition.distance.value = dist
            returnValue.append(f"Bohrung '{feat_name}' auf Tiefe {dist}cm aktualisiert.")
        else:
            # Neu erstellen
            bbox = body.boundingBox
            target_x = params['x'] if params['x'] is not None else (bbox.minPoint.x + bbox.maxPoint.x) / 2.0
            target_y = params['y'] if params['y'] is not None else (bbox.minPoint.y + bbox.maxPoint.y) / 2.0
            
            s = comp.sketches.add(comp.xYConstructionPlane)
            radius_cm = (params['dia_mm'] / 10.0) / 2.0
            s.sketchCurves.sketchCircles.addByCenterRadius(adsk.core.Point3D.create(target_x, target_y, 0), radius_cm)
            prof = s.profiles.item(0)
            
            dist = params['depth']
            if dist <= 0: dist = bbox.maxPoint.z - bbox.minPoint.z + 0.1
            
            ext_input = comp.features.extrudeFeatures.createInput(prof, adsk.fusion.FeatureOperations.CutFeatureOperation)
            ext_input.startExtent = adsk.fusion.OffsetStartDefinition.create(adsk.core.ValueInput.createByReal(bbox.maxPoint.z))
            ext_input.setOneSideExtent(adsk.fusion.DistanceExtentDefinition.create(adsk.core.ValueInput.createByReal(dist)), adsk.fusion.ExtentDirections.NegativeExtentDirection)
            ext_input.participantBodies = [body]
            ext = comp.features.extrudeFeatures.add(ext_input)
            ext.name = feat_name
            returnValue.append(f"Bohrung {params['dia_mm']}mm neu erstellt.")
except Exception as e:
    returnValue.append(f"Error: {str(e)}")
"""
    try:
        res = execute_fusion_script(script, {"dia_mm": diameter_mm, "depth": depth_cm, "body_name": body_name, "x": x_cm, "y": y_cm})
        return res.get("data", ["Error"])[0]
    except FusionBridgeError as e:
        return str(e)

def create_groove_logic(side: str, width_cm: float, depth_cm: float, body_name: str):
    script = """
import adsk.core, adsk.fusion
try:
    d = adsk.fusion.Design.cast(app.activeProduct)
    root = d.rootComponent
    
    def find_body_recursive(component, target_name):
        for b in component.bRepBodies:
            if b.name == target_name or not target_name: return b
        for occ in component.occurrences:
            res = find_body_recursive(occ.component, target_name)
            if res: return res
        return None

    body = find_body_recursive(root, params['body_name'])
    if not body:
        returnValue.append("Error: Body not found.")
    else:
        comp = body.parentComponent
        feat_name = f"FEAT_Groove_{body.name}_{params['side']}"
        existing_feat = comp.features.extrudeFeatures.itemByName(feat_name)
        
        if existing_feat:
            existing_feat.extentDefinition.distance.value = params['d']
            returnValue.append(f"Nut '{feat_name}' auf Tiefe {params['d']}cm aktualisiert.")
        else:
            bbox = body.boundingBox
            side = params['side'].lower()
            w, d_val = params['w'], params['d']
            
            p1 = p2 = None
            if side in ["rechts", "right"]:
                p1 = adsk.core.Point3D.create(bbox.maxPoint.x - w, bbox.minPoint.y, 0)
                p2 = adsk.core.Point3D.create(bbox.maxPoint.x, bbox.maxPoint.y, 0)
            elif side in ["links", "left"]:
                p1 = adsk.core.Point3D.create(bbox.minPoint.x, bbox.minPoint.y, 0)
                p2 = adsk.core.Point3D.create(bbox.minPoint.x + w, bbox.maxPoint.y, 0)
            elif side in ["oben", "top"]:
                p1 = adsk.core.Point3D.create(bbox.minPoint.x, bbox.maxPoint.y - w, 0)
                p2 = adsk.core.Point3D.create(bbox.maxPoint.x, bbox.maxPoint.y, 0)
            elif side in ["unten", "bottom"]:
                p1 = adsk.core.Point3D.create(bbox.minPoint.x, bbox.minPoint.y, 0)
                p2 = adsk.core.Point3D.create(bbox.maxPoint.x, bbox.minPoint.y + w, 0)

            if p1 and p2:
                s = comp.sketches.add(comp.xYConstructionPlane)
                s.sketchCurves.sketchLines.addTwoPointRectangle(p1, p2)
                prof = s.profiles.item(0)
                ext_input = comp.features.extrudeFeatures.createInput(prof, adsk.fusion.FeatureOperations.CutFeatureOperation)
                ext_input.setOneSideExtent(adsk.fusion.DistanceExtentDefinition.create(adsk.core.ValueInput.createByReal(d_val)), adsk.fusion.ExtentDirections.NegativeExtentDirection)
                ext_input.startExtent = adsk.fusion.OffsetStartDefinition.create(adsk.core.ValueInput.createByReal(bbox.maxPoint.z))
                ext_input.participantBodies = [body]
                ext = comp.features.extrudeFeatures.add(ext_input)
                ext.name = feat_name
                returnValue.append(f"Nut auf {side} Seite erstellt.")
except Exception as e:
    returnValue.append(f"Error: {str(e)}")
"""
    try:
        res = execute_fusion_script(script, {"side": side, "w": width_cm, "d": depth_cm, "body_name": body_name})
        return res.get("data", ["Error"])[0]
    except FusionBridgeError as e:
        return str(e)

def register_geometry_tools(mcp):
    # DEUTSCH
    de = I18N["de"]["tools"]
    @mcp.tool(name=de["create_component"]["name"], description=de["create_component"]["description"])
    def komponente_erstellen(name: str) -> str:
        return create_component_logic(name)

    @mcp.tool(name=de["create_sketch"]["name"], description=de["create_sketch"]["description"])
    def skizze_erstellen(ebene: str = "XY", komponenten_name: str = "Root") -> str:
        return create_sketch_logic(ebene, komponenten_name)

    @mcp.tool(name=de["create_box"]["name"], description=de["create_box"]["description"])
    def box_erstellen(laenge_cm: float, breite_cm: float, hoehe_cm: float, name: str = "Brett", x_cm: float = 0, y_cm: float = 0, z_cm: float = 0, operation: str = "NewBody") -> str:
        return create_box_logic(laenge_cm, breite_cm, hoehe_cm, name, x_cm, y_cm, z_cm, operation)

    @mcp.tool(name=de["create_hole"]["name"], description=de["create_hole"]["description"])
    def bohrung_erstellen(durchmesser_mm: float, tiefe_cm: float = 0, koerper_name: str = "", x_cm: float = None, y_cm: float = None) -> str:
        return create_hole_logic(durchmesser_mm, tiefe_cm, koerper_name, x_cm, y_cm)

    @mcp.tool(name=de["create_groove"]["name"], description=de["create_groove"]["description"])
    def nut_erstellen(seite: str, breite_cm: float = 0.5, tiefe_cm: float = 0.5, koerper_name: str = "") -> str:
        return create_groove_logic(seite, breite_cm, tiefe_cm, koerper_name)

    # ENGLISCH
    en = I18N["en"]["tools"]
    @mcp.tool(name=en["create_component"]["name"], description=en["create_component"]["description"])
    def create_component(name: str) -> str:
        return create_component_logic(name)

    @mcp.tool(name=en["create_sketch"]["name"], description=en["create_sketch"]["description"])
    def create_sketch(plane: str = "XY", component_name: str = "Root") -> str:
        return create_sketch_logic(plane, component_name)

    @mcp.tool(name=en["create_box"]["name"], description=en["create_box"]["description"])
    def create_box(length_cm: float, width_cm: float, height_cm: float, name: str = "Board", x_cm: float = 0, y_cm: float = 0, z_cm: float = 0, operation: str = "NewBody") -> str:
        return create_box_logic(length_cm, width_cm, height_cm, name, x_cm, y_cm, z_cm, operation)

    @mcp.tool(name=en["create_hole"]["name"], description=en["create_hole"]["description"])
    def create_hole(diameter_mm: float, depth_cm: float = 0, body_name: str = "", x_cm: float = None, y_cm: float = None) -> str:
        return create_hole_logic(diameter_mm, depth_cm, body_name, x_cm, y_cm)

    @mcp.tool(name=en["create_groove"]["name"], description=en["create_groove"]["description"])
    def create_groove(side: str, width_cm: float = 0.5, depth_cm: float = 0.5, body_name: str = "") -> str:
        return create_groove_logic(side, width_cm, depth_cm, body_name)
