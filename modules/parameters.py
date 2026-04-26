from core.bridge import execute_fusion_script, FusionBridgeError
from core.utils import format_response, register_tool
from modules.parameters_scripts import build_manage_parameter_script

def manage_parameter_logic(name: str, expression: str, unit: str = "mm", comment: str = "", lang: str = "en"):
    """Business logic to add or update a user parameter in Fusion 360."""
    try:
        res = execute_fusion_script(build_manage_parameter_script(), {
            "name": name, "expr": expression, "unit": unit, "comment": comment
        })
        val = res.get("data", ["ERR_UNKNOWN"])[0]
        if val.startswith("ERR_"): return format_response(lang, "parameter_error", val=val)
        if val == "UPDATED": return format_response(lang, "parameter_updated", name=name)
        return format_response(lang, "parameter_created", name=name)
    except FusionBridgeError as e: return f"Error: {str(e)}"

def register_parameter_tools(mcp):
    register_tool(mcp, "manage_parameter", manage_parameter_logic)
