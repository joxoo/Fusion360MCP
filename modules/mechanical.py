from core.bridge import execute_fusion_script, FusionBridgeError
from core.utils import format_response, register_tool
from modules.mechanical_scripts import (
    build_create_bolt_script,
    build_spur_gear_script,
)

def create_bolt_logic(diameter_mm: float, length_cm: float, modeled: bool = True, lang: str = "en"):
    """Business logic for creating a standard ISO bolt."""
    try:
        res = execute_fusion_script(build_create_bolt_script(), {"dia_mm": diameter_mm, "length": length_cm, "modeled": modeled})
        val = res.get("data", ["ERR_UNKNOWN"])[0]
        if val == "ERR_NO_THREAD": return format_response(lang, "no_thread_found", diameter=diameter_mm)
        if val == "ERR_NO_FACE": return format_response(lang, "face_not_found")
        if isinstance(val, str) and val.startswith("ERR_"): return format_response(lang, "unknown_error")
        return format_response(lang, "bolt_created", designation=f"M{val}")
    except FusionBridgeError as e: return f"Error: {str(e)}"

def create_gear_logic(num_teeth: int, module: float, thickness: float = 1.0, x: float = 0, y: float = 0, z: float = 0, hole_diameter: float = 0, pressure_angle: float = 20, lang: str = "en"):
    """Creates a spur gear using an involute-style tooth profile."""
    try:
        res = execute_fusion_script(
            build_spur_gear_script(),
            {"num_teeth": num_teeth, "module": module, "thickness": thickness, "x": x, "y": y, "z": z, "hole_dia": hole_diameter, "pa": pressure_angle},
            use_common=["placement"]
        )
        val = res.get("data", [""])[0]
        if val == "ERR_PARAMS":
            return format_response(lang, "parameter_error", val="num_teeth>=4, module>0, thickness>0 required")
        if isinstance(val, str) and val.startswith("ERR_HOLE_TOO_LARGE:"):
            root_mm = val.split(":", 1)[1]
            return format_response(lang, "parameter_error", val=f"hole_diameter must be smaller than root diameter ({root_mm} mm)")
        if isinstance(val, str) and val.startswith("ERR_"): return val
        return format_response(lang, "gear_created", name=val)
    except FusionBridgeError as e: return f"Error: {str(e)}"

def register_mechanical_tools(mcp):
    register_tool(mcp, "create_bolt", create_bolt_logic)
    register_tool(mcp, "create_gear", create_gear_logic)
