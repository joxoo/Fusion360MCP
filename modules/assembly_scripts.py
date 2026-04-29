def build_create_component_script() -> str:
    return """try:
    name = params.get('name', 'New Component')
    target = resolve_component_context(params.get('component_name'), params.get('component_path'))
    if target:
        occ = target.occurrences.addNewComponent(adsk.core.Matrix3D.create())
        occ.component.name = name
        occ.activate()
        returnValue.append(occ.component.name)
    else:
        returnValue.append("ERR_COMPONENT")
except Exception as e:
    returnValue.append(f"ERR_API:{str(e)}")"""


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


def build_edit_assembly_script() -> str:
    return """
try:
    results = []
    for op in params.get('operations', []):
        action = op.get('action')
        try:
            if action == 'create_component':
                name = op.get('name', 'New Component')
                target = resolve_component_context(op.get('component_name'), op.get('component_path'))
                if target:
                    occ = target.occurrences.addNewComponent(adsk.core.Matrix3D.create())
                    occ.component.name = name
                    results.append(f"{action}:OK:{occ.component.name}")
                else:
                    results.append(f"{action}:ERR_COMPONENT")
            elif action == 'create_joint':
                c1 = find_comp_recursive(root, op['c1'])
                c2 = find_comp_recursive(root, op['c2'])
                if c1 and c2:
                    geo0 = adsk.fusion.JointGeometry.createByPoint(c1.originConstructionPoint)
                    geo1 = adsk.fusion.JointGeometry.createByPoint(c2.originConstructionPoint)
                    joints = root.joints
                    j_in = joints.createInput(geo0, geo1)
                    jt = op.get('type', 'Rigid').lower()
                    if jt == "revolute": j_in.setAsRevoluteJointMotion(adsk.fusion.JointDirections.ZAxisJointDirection)
                    elif jt == "slider": j_in.setAsSliderJointMotion(adsk.fusion.JointDirections.ZAxisJointDirection)
                    else: j_in.setAsRigidJointMotion()
                    joints.add(j_in)
                    results.append(f"{action}:OK")
                else:
                    results.append(f"{action}:ERR_COMP")
            else:
                results.append(f"{action}:ERR_UNKNOWN_ACTION")
        except Exception as e:
            results.append(f"{action}:ERR:{str(e)}")
    returnValue.append(",".join(results) if results else "OK")
except Exception as e:
    returnValue.append(f"ERR_API:{str(e)}")
"""

