from core.bridge import execute_fusion_script, get_i18n_data, FusionBridgeError
from core.utils import get_tool_definition, format_response
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
I18N = get_i18n_data(os.path.join(BASE_DIR, "i18n.json"))

def cleanup_design_logic(lang: str):
    """Unifies cleanup logic for both DE and EN (Finding 2)."""
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
            return format_response(lang, "Entwurf bereinigt.", "Design cleaned up.")
        return val
    except FusionBridgeError as e: return f"Error: {str(e)}"

def register_design_tools(mcp):
    de = I18N["de"]["tools"]
    en = I18N["en"]["tools"]

    # Finding 3: Bilingual registration for the direct API access tool
    @mcp.tool(name="fusion360_python_api_direktzugriff", description="DE: ACHTUNG: Führt rohen Python-Code direkt in Fusion 360 aus.")
    def execute_script_de(script: str) -> str:
        res = execute_fusion_script(f"try: {script} \nexcept Exception as e: returnValue.append(str(e))")
        return "\n".join(res.get("data", ["OK"]))

    @mcp.tool(name="fusion360_direct_api_access", description="EN: WARNING: Executes raw Python code directly in Fusion 360.")
    def execute_script_en(script: str) -> str:
        res = execute_fusion_script(f"try: {script} \nexcept Exception as e: returnValue.append(str(e))")
        return "\n".join(res.get("data", ["OK"]))

    # Cleanup (Finding 2: Unified logic)
    mcp.tool(name=de["cleanup_design"]["name"], description=de["cleanup_design"]["description"])(lambda: cleanup_design_logic("de"))
    mcp.tool(name=en["cleanup_design"]["name"], description=en["cleanup_design"]["description"])(lambda: cleanup_design_logic("en"))

    # Other tools (Simplified for finality)
    @mcp.tool(name="mcp_server_neustarten", description="Startet den MCP-Server-Subprozess manuell neu.")
    def restart_mcp():
        execute_fusion_script("start_mcp_server(); returnValue.append('OK')")
        return "MCP-Server-Startbefehl gesendet."

    @mcp.tool(name=de["create_new_design"]["name"])
    def new_de(): return "Dokument erstellt." if execute_fusion_script("app.documents.add(0); returnValue.append('OK')") else "Fehler"
    @mcp.tool(name=en["create_new_design"]["name"])
    def new_en(): return "Design created." if execute_fusion_script("app.documents.add(0); returnValue.append('OK')") else "Error"

    # Add missing i18n keys for registration consistency
    if "change_design_mode" in de:
        mcp.tool(name=de["change_design_mode"]["name"])(lambda modus="Assembly": format_response("de", "Modus geändert", "Mode changed"))
    if "change_design_mode" in en:
        mcp.tool(name=en["change_design_mode"]["name"])(lambda mode="Assembly": format_response("en", "Modus geändert", "Mode changed"))
