from core.bridge import execute_fusion_script, FusionBridgeError
from core.utils import register_tool
from core.error_handler import bridge_error_message, get_result_value
from modules.export_scripts import build_export_stl_script, build_export_project_script
from modules.advanced_geometry_scripts import build_export_step_script


def export_model_logic(format: str, filename: str = "model", lang: str = "en"):
    """Exports the current design in the requested format."""
    export_format = str(format).lower()
    exporters = {
        "stl": build_export_stl_script,
        "f3d": build_export_project_script,
        "step": build_export_step_script,
    }
    builder = exporters.get(export_format)
    if not builder:
        return f"Error: Unsupported export format '{format}'. Supported formats: stl, f3d, step."

    try:
        res = execute_fusion_script(builder(), {"filename": filename})
        return get_result_value(res, "Error")
    except FusionBridgeError as e:
        return bridge_error_message(e)

def register_export_tools(mcp):
    register_tool(mcp, "export_model", export_model_logic)
