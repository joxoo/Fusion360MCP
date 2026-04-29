from core.bridge import execute_fusion_script, FusionBridgeError
from core.utils import format_response, register_tool
from core.error_handler import bridge_error_message, get_result_value, localized_error, map_result_error
from modules.mechanical_scripts import (
    build_create_bolt_script,
    build_spur_gear_script,
)

def create_bolt_logic(diameter_mm: float, length_cm: float, modeled: bool = True, lang: str = "en", component_name: str = None, component_path: str = None):
    """Business logic for creating a standard ISO bolt."""
    try:
        res = execute_fusion_script(build_create_bolt_script(), {
            "dia_mm": diameter_mm, "length": length_cm, "modeled": modeled,
            "component_name": component_name, "component_path": component_path
        }, use_common=["find_body"])
        val = get_result_value(res, "ERR_UNKNOWN")
        mapped_error = map_result_error(val, lang, {
            "ERR_COMPONENT": localized_error("component_not_found"),
            "ERR_NO_THREAD": localized_error("no_thread_found", diameter=diameter_mm),
            "ERR_NO_FACE": localized_error("face_not_found"),
            "ERR_VERIFICATION_FAILED": "Error: Geometry verification failed. The body was not created or is not visible.",
        }, passthrough_err_prefix=False)
        if mapped_error:
            return mapped_error
        if isinstance(val, str) and val.startswith("ERR_"):
            return format_response(lang, "unknown_error")
        return format_response(lang, "bolt_created", designation=f"M{val}")
    except FusionBridgeError as e: return bridge_error_message(e)

def create_gear_logic(num_teeth: int, module: float, thickness: float = 1.0, x: float = 0, y: float = 0, z: float = 0, hole_diameter: float = 0, pressure_angle: float = 20, lang: str = "en", component_name: str = None, component_path: str = None):
    """Creates a spur gear using an involute-style tooth profile."""
    try:
        res = execute_fusion_script(
            build_spur_gear_script(),
            {
                "num_teeth": num_teeth, "module": module, "thickness": thickness,
                "x": x, "y": y, "z": z, "hole_dia": hole_diameter, "pa": pressure_angle,
                "component_name": component_name, "component_path": component_path
            },
            use_common=["placement", "find_body"]
        )
        val = get_result_value(res)
        mapped_error = map_result_error(val, lang, {
            "ERR_COMPONENT": localized_error("component_not_found"),
            "ERR_PARAMS": localized_error("parameter_error", val="num_teeth>=4, module>0, thickness>0 required"),
            "ERR_VERIFICATION_FAILED": "Error: Geometry verification failed. The body was not created or is not visible.",
        }, passthrough_err_prefix=False)
        if mapped_error:
            return mapped_error
        if isinstance(val, str) and val.startswith("ERR_HOLE_TOO_LARGE:"):
            root_mm = val.split(":", 1)[1]
            return format_response(lang, "parameter_error", val=f"hole_diameter must be smaller than root diameter ({root_mm} mm)")
        if isinstance(val, str) and val.startswith("ERR_"): return val
        return format_response(lang, "gear_created", name=val)
    except FusionBridgeError as e: return bridge_error_message(e)

def register_mechanical_tools(mcp):
    register_tool(mcp, "create_bolt", create_bolt_logic)
    register_tool(mcp, "create_gear", create_gear_logic)
