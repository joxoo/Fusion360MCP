from core.bridge import execute_fusion_script, FusionBridgeError
from core.utils import format_response, register_tool
from modules.export_scripts import build_export_stl_script, build_export_project_script

def export_stl_logic(filename: str = "model", lang: str = "en"):
    """Exports the model as STL for 3D printing."""
    try:
        res = execute_fusion_script(build_export_stl_script(), {"filename": filename})
        return res.get("data", ["Error"])[0]
    except FusionBridgeError as e: return f"Error: {str(e)}"

def export_project_logic(filename: str = "archive", lang: str = "en"):
    """Exports the full project as F3D archive."""
    try:
        res = execute_fusion_script(build_export_project_script(), {"filename": filename})
        return res.get("data", ["Error"])[0]
    except FusionBridgeError as e: return f"Error: {str(e)}"

def register_export_tools(mcp):
    register_tool(mcp, "export_stl", export_stl_logic)
    register_tool(mcp, "export_f3d", export_project_logic)
