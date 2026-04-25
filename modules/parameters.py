from core.bridge import execute_fusion_script, FusionBridgeError
from core.utils import format_response, register_tool

def manage_parameter_logic(name: str, expression: str, unit: str = "mm", comment: str = "", lang: str = "en"):
    """Business logic to add or update a user parameter in Fusion 360."""
    script = """
try:
    params_coll = d.userParameters
    existing = params_coll.itemByName(params['name'])
    if existing:
        existing.expression = params['expr']
        returnValue.append("UPDATED")
    else:
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
        if val.startswith("ERR_"): return format_response(lang, "parameter_error", val=val)
        if val == "UPDATED": return format_response(lang, "parameter_updated", name=name)
        return format_response(lang, "parameter_created", name=name)
    except FusionBridgeError as e: return f"Error: {str(e)}"

def register_parameter_tools(mcp):
    register_tool(mcp, "manage_parameter", manage_parameter_logic)
