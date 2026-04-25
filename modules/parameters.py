from core.bridge import execute_fusion_script, get_i18n_data, FusionBridgeError
from core.utils import get_tool_definition, format_response
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
I18N = get_i18n_data(os.path.join(BASE_DIR, "i18n.json"))

def manage_parameter_logic(name: str, expression: str, unit: str, comment: str, lang: str):
    """Business logic to add or update a user parameter in Fusion 360."""
    script = """
try:
    params_coll = d.userParameters
    existing = params_coll.itemByName(params['name'])
    
    if existing:
        existing.expression = params['expr']
        returnValue.append("UPDATED")
    else:
        # add(name, valueInput, unit, comment)
        val = adsk.core.ValueInput.createByString(params['expr'])
        params_coll.add(params['name'], val, params['unit'], params['comment'])
        returnValue.append("CREATED")
except Exception as e:
    returnValue.append(f"ERR_API:{str(e)}")
"""
    try:
        res = execute_fusion_script(script, {
            "name": name, "expr": expression, "unit": unit, "comment": comment
        })
        val = res.get("data", ["ERR_UNKNOWN"])[0]
        
        if val.startswith("ERR_"):
            return format_response(lang, "Parameter-Fehler: {val}", "Parameter error: {val}", val=val)
        
        if val == "UPDATED":
            return format_response(lang, f"Parameter '{name}' aktualisiert.", f"Parameter '{name}' updated.")
        return format_response(lang, f"Parameter '{name}' erstellt.", f"Parameter '{name}' created.")
    except FusionBridgeError as e: return f"Error: {str(e)}"

def register_parameter_tools(mcp):
    # DEUTSCH
    @mcp.tool(name="parameter_verwalten", description="Erstellt oder aktualisiert einen Benutzerparameter (z.B. Name='Wand', Ausdruck='5mm').")
    def param_de(name: str, ausdruck: str, einheit: str = "mm", kommentar: str = ""):
        return manage_parameter_logic(name, ausdruck, einheit, kommentar, "de")

    # ENGLISCH
    @mcp.tool(name="manage_parameter", description="Creates or updates a user parameter (e.g., name='Wall', expression='5mm').")
    def param_en(name: str, expression: str, unit: str = "mm", comment: str = ""):
        return manage_parameter_logic(name, expression, unit, comment, "en")
