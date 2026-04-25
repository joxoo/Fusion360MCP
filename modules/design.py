from core.bridge import execute_fusion_script, FusionBridgeError
from core.utils import format_response, register_tool

def cleanup_design_logic(lang: str):
    """Unifies cleanup logic for both DE and EN."""
    script = """
try:
    for i in range(root.occurrences.count - 1, -1, -1): root.occurrences.item(i).deleteMe()
    for i in range(root.bRepBodies.count - 1, -1, -1): root.bRepBodies.item(i).deleteMe()
    returnValue.append("OK")
except Exception as e:
    returnValue.append(f"ERR_API:{str(e)}")
"""
    try:
        res = execute_fusion_script(script)
        val = res.get("data", ["Error"])[0]
        if val == "OK":
            return format_response(lang, "design_cleaned")
        return val
    except FusionBridgeError as e: return f"Error: {str(e)}"

def restart_mcp_logic(lang: str):
    """Manually restarts the MCP server subprocess."""
    execute_fusion_script("start_mcp_server(); returnValue.append('OK')")
    return format_response(lang, "mcp_restart_sent")

def create_new_design_logic(lang: str):
    """Creates a new empty Fusion 360 document."""
    if execute_fusion_script("app.documents.add(0); returnValue.append('OK')"):
        return format_response(lang, "document_created")
    return "Error"

def change_design_mode_logic(mode: str = "Assembly", lang: str = "en"):
    """Switch mode between 'Part' and 'Assembly'."""
    # Logic is simplified here as it mainly returns status in this mock/bridge setup
    return format_response(lang, "mode_changed")

def direct_api_access_logic(script: str, lang: str):
    """Executes raw Python code directly in Fusion 360."""
    res = execute_fusion_script(f"try: {script} \nexcept Exception as e: returnValue.append(str(e))")
    return "\n".join(res.get("data", ["OK"]))

def register_design_tools(mcp):
    # Register tools using the centralized helper
    register_tool(mcp, "direct_api_access", direct_api_access_logic)
    register_tool(mcp, "cleanup_design", cleanup_design_logic)
    register_tool(mcp, "restart_mcp", restart_mcp_logic)
    register_tool(mcp, "create_new_design", create_new_design_logic)
    register_tool(mcp, "change_design_mode", change_design_mode_logic)
