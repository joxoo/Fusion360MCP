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
    def resolve_joint_component(payload, name_key, path_key, legacy_key):
        comp = resolve_component_context(payload.get(name_key), payload.get(path_key))
        if comp:
            return comp
        legacy_name = payload.get(legacy_key)
        if legacy_name:
            return resolve_component_context(legacy_name, None)
        return None

    c1 = resolve_joint_component(params, 'component1_name', 'component1_path', 'c1')
    c2 = resolve_joint_component(params, 'component2_name', 'component2_path', 'c2')

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
    else: returnValue.append("ERR_COMPONENT")
except Exception as e:
    returnValue.append(f"ERR_API:{str(e)}")"""


def build_edit_assembly_script() -> str:
    return """
try:
    def resolve_joint_component(payload, name_key, path_key, legacy_key):
        comp = resolve_component_context(payload.get(name_key), payload.get(path_key))
        if comp:
            return comp
        legacy_name = payload.get(legacy_key)
        if legacy_name:
            return resolve_component_context(legacy_name, None)
        return None

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
                    occ.activate()
                    created = resolve_component_context(occ.component.name, None)
                    if created:
                        results.append(f"{action}:OK:{occ.component.name}")
                    else:
                        results.append(f"{action}:ERR_VERIFICATION_FAILED")
                else:
                    results.append(f"{action}:ERR_COMPONENT")
            elif action == 'create_joint':
                c1 = resolve_joint_component(op, 'component1_name', 'component1_path', 'c1')
                c2 = resolve_joint_component(op, 'component2_name', 'component2_path', 'c2')
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
                    results.append(f"{action}:ERR_COMPONENT")
            else:
                results.append(f"{action}:ERR_UNKNOWN_ACTION")
        except Exception as e:
            results.append(f"{action}:ERR:{str(e)}")
    returnValue.append(",".join(results) if results else "OK")
except Exception as e:
    returnValue.append(f"ERR_API:{str(e)}")
"""
