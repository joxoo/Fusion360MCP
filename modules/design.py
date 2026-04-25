from core.bridge import execute_fusion_script, get_i18n_data, FusionBridgeError
import os
import json

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
I18N_PATH = os.path.join(BASE_DIR, "i18n.json")
I18N = get_i18n_data(I18N_PATH)

def get_timeline_logic():
    script = """
import json
design = adsk.fusion.Design.cast(app.activeProduct)
timeline = design.timeline
history = []

# Map health states to readable strings
health_map = {
    0: "Healthy",
    1: "Warning",
    2: "Error"
}

for i in range(timeline.count):
    obj = timeline.item(i)
    name = "Unnamed"
    obj_type = "Unknown"
    
    if obj.entity:
        try:
            name = obj.entity.name
            obj_type = obj.entity.objectType.split('::')[-1]
        except:
            pass
            
    history.append({
        "index": i,
        "name": name,
        "type": obj_type,
        "status": health_map.get(obj.healthState, "Unknown"),
        "isSuppressed": obj.isSuppressed
    })

returnValue.append(json.dumps(history))
"""
    try:
        res = execute_fusion_script(script)
        return res.get("data", ["[]"])[0]
    except FusionBridgeError as e:
        return str(e)

def register_design_tools(mcp):
    # DEUTSCH
    de = I18N["de"]["tools"]
    
    @mcp.tool(name="design_modus_aendern", description="Stellt den Modus auf 'Bauteil' (Part) oder 'Baugruppe' (Assembly) um.")
    def design_modus_aendern(modus: str = "Assembly") -> str:
        script = f"""
d = adsk.fusion.Design.cast(app.activeProduct)
try:
    if params['modus'] == "Assembly":
        d.designIntent = adsk.fusion.DesignIntents.AssemblyDesignIntent
    else:
        d.designIntent = adsk.fusion.DesignIntents.PartDesignIntent
    returnValue.append(f"Modus auf {{params['modus']}} ge\u00e4ndert.")
except Exception as e:
    returnValue.append(str(e))
"""
        try:
            res = execute_fusion_script(script, {"modus": modus})
            return res.get("data", ["Error"])[0]
        except FusionBridgeError as e:
            return str(e)

    @mcp.tool(name=de["create_new_design"]["name"], description=de["create_new_design"]["description"])
    def neue_konstruktion() -> str:
        script = "doc = app.documents.add(adsk.core.DocumentTypes.FusionDesignDocumentType); returnValue.append('Neues Dokument erstellt.')"
        try:
            res = execute_fusion_script(script)
            return res.get("data", ["Fehler"])[0]
        except FusionBridgeError as e:
            return str(e)

    @mcp.tool(name=de["cleanup_design"]["name"], description=de["cleanup_design"]["description"])
    def design_bereinigen() -> str:
        script = """
c = app.activeProduct.rootComponent
for i in range(c.occurrences.count - 1, -1, -1): c.occurrences.item(i).deleteMe()
for i in range(c.bRepBodies.count - 1, -1, -1): c.bRepBodies.item(i).deleteMe()
for i in range(c.sketches.count - 1, -1, -1): c.sketches.item(i).deleteMe()
for i in range(c.constructionPlanes.count - 1, -1, -1):
    try: c.constructionPlanes.item(i).deleteMe()
    except: pass
returnValue.append('Bereinigt')
"""
        try:
            res = execute_fusion_script(script)
            return res.get("data", ["Done"])[0]
        except FusionBridgeError as e:
            return str(e)

    @mcp.tool(name=de["get_timeline"]["name"], description=de["get_timeline"]["description"])
    def bearbeitungshistorie_anzeigen() -> str:
        return get_timeline_logic()

    # ENGLISCH
    en = I18N["en"]["tools"]
    @mcp.tool(name="change_design_mode", description="Switch mode between 'Part' and 'Assembly'.")
    def change_design_mode(mode: str = "Assembly") -> str:
        return design_modus_aendern(mode)

    @mcp.tool(name=en["get_timeline"]["name"], description=en["get_timeline"]["description"])
    def get_timeline() -> str:
        return get_timeline_logic()
