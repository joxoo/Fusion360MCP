from core.bridge import execute_fusion_script, get_i18n_data, FusionBridgeError
from core.utils import get_tool_definition, format_response
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
I18N = get_i18n_data(os.path.join(BASE_DIR, "i18n.json"))

def create_joint_logic(comp1: str, comp2: str, joint_type: str, lang: str):
    """Creates a joint between two components."""
    script = """
try:
    # 1. Find Components
    c1 = find_comp_recursive(root, params['c1'])
    c2 = find_comp_recursive(root, params['c2'])
    
    if c1 and c2:
        # 2. Create Joint Geometry (at origin for now)
        geo0 = adsk.fusion.JointGeometry.createByPoint(c1.originConstructionPoint)
        geo1 = adsk.fusion.JointGeometry.createByPoint(c2.originConstructionPoint)
        
        # 3. Create Joint Input
        joints = root.joints
        j_in = joints.createInput(geo0, geo1)
        
        # 4. Set Type
        jt = params['type'].lower()
        if jt == "revolute": j_in.setAsRevoluteJointMotion(adsk.fusion.JointDirections.ZAxisJointDirection)
        elif jt == "slider": j_in.setAsSliderJointMotion(adsk.fusion.JointDirections.ZAxisJointDirection)
        else: j_in.setAsRigidJointMotion()
        
        joints.add(j_in)
        returnValue.append("OK")
    else: returnValue.append("ERR_COMP")
except Exception as e:
    returnValue.append(f"ERR_API:{str(e)}")
"""
    try:
        res = execute_fusion_script(script, {"c1":comp1, "c2":comp2, "type":joint_type}, use_common=["find_comp"])
        val = res.get("data", [""])[0]
        if val == "ERR_COMP": return format_response(lang, "Komponenten nicht gefunden.", "Components not found.")
        return format_response(lang, f"Gelenk ({joint_type}) erstellt.", f"Joint ({joint_type}) created.")
    except FusionBridgeError as e: return f"Error: {str(e)}"

def register_assembly_tools(mcp):
    # DEUTSCH
    @mcp.tool(name="gelenk_erstellen", description="Verbindet zwei Komponenten (z.B. Rigid, Revolute, Slider).")
    def joint_de(komponente1: str, komponente2: str, typ: str = "Rigid"):
        return create_joint_logic(komponente1, komponente2, typ, "de")

    # ENGLISCH
    @mcp.tool(name="create_joint", description="Connects two components with a joint (e.g., Rigid, Revolute, Slider).")
    def joint_en(component1: str, component2: str, type: str = "Rigid"):
        return create_joint_logic(component1, component2, type, "en")
