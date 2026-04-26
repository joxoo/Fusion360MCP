def build_create_joint_script() -> str:
    return """try:
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
    returnValue.append(f"ERR_API:{str(e)}")"""
