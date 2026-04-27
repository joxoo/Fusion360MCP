from core.bridge import execute_fusion_script, FusionBridgeError
from core.utils import format_response, register_tool
from modules.assembly_scripts import build_create_joint_script, build_create_component_script

def create_component_logic(name: str = "New Component", lang: str = "en"):
    """Creates a new empty component in the root design."""
    try:
        res = execute_fusion_script(build_create_component_script(), {"name": name})
        val = res.get("data", [""])[0]
        if isinstance(val, str) and val.startswith("ERR_"): return val
        return f"Component '{val}' created."
    except FusionBridgeError as e: return f"Error: {str(e)}"

def create_joint_logic(comp1: str, comp2: str, joint_type: str = "Rigid", lang: str = "en"):
    """Creates a joint between two components."""
    try:
        res = execute_fusion_script(build_create_joint_script(), {"c1":comp1, "c2":comp2, "type":joint_type}, use_common=["find_comp"])
        val = res.get("data", [""])[0]
        if val == "ERR_COMP": return format_response(lang, "components_not_found")
        return format_response(lang, "joint_created", type=joint_type)
    except FusionBridgeError as e: return f"Error: {str(e)}"

def register_assembly_tools(mcp):
    register_tool(mcp, "create_component", create_component_logic)
    register_tool(mcp, "create_joint", create_joint_logic)
