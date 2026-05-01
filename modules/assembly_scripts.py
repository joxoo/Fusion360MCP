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
    def normalize_component_path(path_value):
        if not path_value:
            return ""
        path_text = str(path_value).strip().replace("\\\\", "/")
        if path_text.startswith("/"):
            path_text = path_text[1:]
        return path_text

    def resolve_occurrence_by_reference(component_name=None, component_path=None):
        component_path = normalize_component_path(component_path)
        if component_path:
            if component_path == "Root":
                return None, "ERR_ROOT_COMPONENT"
            if component_path.startswith("Root/"):
                component_path = component_path[5:]
            current = root
            occurrence = None
            for segment in [part for part in component_path.split("/") if part]:
                occurrence = None
                for occ in current.occurrences:
                    occ_name = getattr(occ, 'name', '')
                    comp_name = getattr(occ.component, 'name', '')
                    if occ_name == segment or comp_name == segment:
                        occurrence = occ
                        current = occ.component
                        break
                if occurrence is None:
                    return None, "ERR_COMPONENT"
            return occurrence, None

        if component_name:
            if str(component_name).strip() == "Root":
                return None, "ERR_ROOT_COMPONENT"
            for occ in root.allOccurrences:
                occ_name = getattr(occ, 'name', '')
                comp_name = getattr(occ.component, 'name', '')
                if occ_name == component_name or comp_name == component_name:
                    return occ, None
            return None, "ERR_COMPONENT"

        return None, "ERR_COMPONENT"

    def resolve_target_occurrence(payload):
        return resolve_occurrence_by_reference(
            payload.get('target_component_name') or payload.get('component_name'),
            payload.get('target_component_path') or payload.get('component_path'),
        )

    def resolve_joint_occurrence(payload, name_key, path_key, legacy_key):
        occurrence, occ_err = resolve_occurrence_by_reference(
            payload.get(name_key),
            payload.get(path_key),
        )
        if occurrence:
            return occurrence, None
        legacy_name = payload.get(legacy_key)
        if legacy_name:
            return resolve_occurrence_by_reference(legacy_name, None)
        return None, occ_err or "ERR_COMPONENT"

    def parse_bool(value, default_value=True):
        if value is None:
            return default_value
        if isinstance(value, bool):
            return value
        if isinstance(value, (int, float)):
            return value != 0
        text = str(value).strip().lower()
        if text in ("true", "1", "yes", "on"):
            return True
        if text in ("false", "0", "no", "off"):
            return False
        return default_value

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
            elif action == 'rename_component':
                occurrence, occ_err = resolve_target_occurrence(op)
                if occ_err:
                    results.append(f"{action}:{occ_err}")
                else:
                    new_name = op.get('new_name')
                    if not new_name:
                        results.append(f"{action}:ERR_NEW_NAME_REQUIRED")
                    else:
                        occurrence.component.name = str(new_name)
                        results.append(f"{action}:OK:{occurrence.component.name}")
            elif action == 'delete_component':
                occurrence, occ_err = resolve_target_occurrence(op)
                if occ_err:
                    results.append(f"{action}:{occ_err}")
                else:
                    occurrence.deleteMe()
                    results.append(f"{action}:OK")
            elif action == 'move_component':
                occurrence, occ_err = resolve_target_occurrence(op)
                if occ_err:
                    results.append(f"{action}:{occ_err}")
                else:
                    transform = adsk.core.Matrix3D.create()
                    current_transform = occurrence.transform2 if hasattr(occurrence, 'transform2') else occurrence.transform
                    transform.copy(current_transform)
                    current_translation = transform.translation
                    translation = adsk.core.Vector3D.create(
                        current_translation.x + float(op.get('x', 0)),
                        current_translation.y + float(op.get('y', 0)),
                        current_translation.z + float(op.get('z', 0))
                    )
                    transform.translation = translation
                    if hasattr(occurrence, 'transform2'):
                        occurrence.transform2 = transform
                    else:
                        occurrence.transform = transform
                    results.append(f"{action}:OK")
            elif action == 'create_as_built_joint':
                occ1, occ1_err = resolve_joint_occurrence(op, 'component1_name', 'component1_path', 'c1')
                occ2, occ2_err = resolve_joint_occurrence(op, 'component2_name', 'component2_path', 'c2')
                if occ1 and occ2:
                    joints = root.asBuiltJoints
                    j_in = joints.createInput(occ1, occ2, None)
                    jt = op.get('type', 'Rigid').lower()
                    if jt == "revolute": j_in.setAsRevoluteJointMotion(adsk.fusion.JointDirections.ZAxisJointDirection)
                    elif jt == "slider": j_in.setAsSliderJointMotion(adsk.fusion.JointDirections.ZAxisJointDirection)
                    else: j_in.setAsRigidJointMotion()
                    joints.add(j_in)
                    results.append(f"{action}:OK")
                else:
                    results.append(f"{action}:{occ1_err or occ2_err or 'ERR_COMPONENT'}")
            elif action == 'set_contact_sets':
                design = adsk.fusion.Design.cast(app.activeProduct)
                enable = parse_bool(op.get('enable'), True)
                design.isContactAnalysisEnabled = enable
                results.append(f"{action}:OK:{enable}")
            else:
                results.append(f"{action}:ERR_UNKNOWN_ACTION")
        except Exception as e:
            results.append(f"{action}:ERR:{str(e)}")
    returnValue.append(",".join(results) if results else "OK")
except Exception as e:
    returnValue.append(f"ERR_API:{str(e)}")
"""
