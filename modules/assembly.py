from core.bridge import execute_fusion_script, FusionBridgeError
from core.utils import format_response, register_tool

def create_joint_logic(comp1: str, comp2: str, joint_type: str = "Rigid", lang: str = "en"):
    """Creates a joint between two components."""
    script = """
try:
    c1 = find_comp_recursive(root, params['c1'])
    c2 = find_comp_recursive(root, params['c2'])
    
    if c1 and c2:
        geo0 = adsk.fusion.JointGeometry.createByPoint(c1.originConstructionPoint)
        geo1 = adsk.fusion.JointGeometry.createByPoint(c2.originConstructionPoint)
        joints = root.joints
        j_in = joints.createInput(geo0, geo1)
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
        if val == "ERR_COMP": return format_response(lang, "components_not_found")
        return format_response(lang, "joint_created", type=joint_type)
    except FusionBridgeError as e: return f"Error: {str(e)}"

def register_assembly_tools(mcp):
    register_tool(mcp, "create_joint", create_joint_logic)
