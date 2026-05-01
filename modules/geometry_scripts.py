import json

def build_create_chamfer_script() -> str:
    return """try:
    target = find_body_recursive(root, params['body'])
    if target:
        edges = adsk.core.ObjectCollection.create()
        for e in target.edges: edges.add(e)
        chamfers = target.parentComponent.features.chamferFeatures
        c_in = chamfers.createInput(edges, True)
        c_in.setToEqualDistance(adsk.core.ValueInput.createByReal(params['dist']))
        chamfers.add(c_in)
        returnValue.append("OK")
    else: returnValue.append("ERROR")
except Exception as e:
    returnValue.append(f"ERR_API:{str(e)}")"""


def build_create_shell_script() -> str:
    return """try:
    target = find_body_recursive(root, params['body'])
    if target:
        face = next((f for f in target.faces if f.geometry.surfaceType == adsk.core.SurfaceTypes.PlaneSurfaceType), target.faces.item(0))
        faces = adsk.core.ObjectCollection.create(); faces.add(face)
        shells = target.parentComponent.features.shellFeatures
        s_in = shells.createInput(faces, False)
        s_in.insideThickness = adsk.core.ValueInput.createByReal(params['thick'])
        shells.add(s_in)
        returnValue.append("OK")
    else: returnValue.append("ERROR")
except Exception as e:
    returnValue.append(f"ERR_API:{str(e)}")"""


def build_mirror_body_script() -> str:
    return """try:
    target = find_body_recursive(root, params['body'])
    plane = {"XY": active_comp.xYConstructionPlane, "XZ": active_comp.xZConstructionPlane, "YZ": active_comp.yZConstructionPlane}.get(params['plane'], active_comp.xYConstructionPlane)
    if target:
        ents = adsk.core.ObjectCollection.create(); ents.add(target)
        mirrors = active_comp.features.mirrorFeatures
        m_in = mirrors.createInput(ents, plane)
        mirrors.add(m_in)
        returnValue.append("OK")
    else: returnValue.append("ERROR")
except Exception as e:
    returnValue.append(f"ERR_API:{str(e)}")"""


def build_create_revolve_script() -> str:
    return """try:
    s = find_sketch_recursive(root, params['sketch'])
    axis_entity = {"X": active_comp.xConstructionAxis, "Y": active_comp.yConstructionAxis, "Z": active_comp.zConstructionAxis}.get(params['axis'], active_comp.zConstructionAxis)
    if s and s.profiles.count > 0:
        prof = s.profiles.item(0)
        revolves = active_comp.features.revolveFeatures
        rev_in = revolves.createInput(prof, axis_entity, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
        angle = adsk.core.ValueInput.createByString(f"{params['angle']} deg")
        rev_in.setAngleExtent(False, angle)
        rev_feat = revolves.add(rev_in)
        returnValue.append(rev_feat.bodies.item(0).name)
    else: returnValue.append("ERR_SKETCH")
except Exception as e:
    returnValue.append(f"ERR_API:{str(e)}")"""


def build_create_boundary_fill_script() -> str:
    return """try:
    tool_collection = adsk.core.ObjectCollection.create()
    for name in params['tool_bodies']:
        t = find_body_recursive(root, name)
        if t: tool_collection.add(t)
    
    if tool_collection.count > 0:
        bfills = active_comp.features.boundaryFillFeatures
        bf_in = bfills.createInput(tool_collection, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
        # Select all cells by default to create the solid
        for cell in bf_in.bRepCells:
            cell.isSelected = True
        bf_feat = bfills.add(bf_in)
        returnValue.append(bf_feat.bodies.item(0).name)
    else: returnValue.append("ERR_TOOLS")
except Exception as e:
    returnValue.append(f"ERR_API:{str(e)}")"""


def build_create_sweep_script() -> str:
    return """try:
    profile_sk, owner_comp, profile_err = resolve_sketch_context(
        params['profile_sketch'],
        params.get('component_name'),
        params.get('component_path')
    )
    path_sk, path_owner, path_err = resolve_sketch_context(
        params['path_sketch'],
        params.get('component_name'),
        params.get('component_path')
    )

    if profile_err == "ERR_COMPONENT" or path_err == "ERR_COMPONENT":
        returnValue.append("ERR_COMPONENT")
    elif profile_sk and path_sk and owner_comp != path_owner:
        returnValue.append("ERR_OWNER_MISMATCH")
    elif profile_sk and path_sk and profile_sk.profiles.count > 0 and path_sk.sketchCurves.count > 0:
        prof = profile_sk.profiles.item(0)
        sweeps = owner_comp.features.sweepFeatures
        path = owner_comp.features.createPath(path_sk.sketchCurves.item(0))
        rev_op = adsk.fusion.FeatureOperations.NewBodyFeatureOperation
        s_in = sweeps.createInput(prof, path, rev_op)
        if params.get('twist', 0) != 0:
            s_in.twistAngle = adsk.core.ValueInput.createByString(f"{params['twist']} deg")
        s_feat = sweeps.add(s_in)
        returnValue.append(s_feat.name)
    else: returnValue.append("ERR_INPUT")
except Exception as e:
    returnValue.append(f"ERR_API:{str(e)}")"""


def build_create_feature_pattern_script() -> str:
    return """try:
    target_name = params['feature_name']
    feature = None
    
    # Check common feature types
    collections = [
        active_comp.features.extrudeFeatures,
        active_comp.features.revolveFeatures,
        active_comp.features.sweepFeatures,
        active_comp.features.holeFeatures,
        active_comp.features.filletFeatures,
        active_comp.features.chamferFeatures
    ]
    
    for coll in collections:
        for f in coll:
            if f.name == target_name:
                feature = f
                break
        if feature: break
        
    if feature:
        ents = adsk.core.ObjectCollection.create()
        ents.add(feature)
        axis = {"X": active_comp.xConstructionAxis, "Y": active_comp.yConstructionAxis, "Z": active_comp.zConstructionAxis}.get(params['axis'], active_comp.zConstructionAxis)
        
        patterns = active_comp.features.circularPatternFeatures
        p_in = patterns.createInput(ents, axis)
        p_in.quantity = adsk.core.ValueInput.createByReal(params['count'])
        p_feat = patterns.add(p_in)
        returnValue.append("OK")
    else: returnValue.append("ERR_FEATURE_NOT_FOUND")
except Exception as e:
    returnValue.append(f"ERR_API:{str(e)}")"""


def build_create_hole_advanced_script() -> str:
    return """try:
    # Find the target face for placement
    target_body = find_body_recursive(root, params['body'])
    if not target_body:
        returnValue.append("ERR_BODY")
    else:
        # Simple placement logic: find a face or use the provided Z
        face = next((f for f in target_body.faces if f.geometry.surfaceType == adsk.core.SurfaceTypes.PlaneSurfaceType), target_body.faces.item(0))
        hole_feats = active_comp.features.holeFeatures
        
        # Determine hole type and create input
        h_type = params.get('hole_type', 'Simple').lower()
        h_dia = adsk.core.ValueInput.createByReal(params['dia'] / 10.0)
        
        if h_type == 'counterbore':
            cb_dia = adsk.core.ValueInput.createByReal(params['cb_dia'] / 10.0)
            cb_depth = adsk.core.ValueInput.createByReal(params['cb_depth'] / 10.0)
            h_in = hole_feats.createCounterboreInput(h_dia, cb_dia, cb_depth)
        elif h_type == 'countersink':
            cs_dia = adsk.core.ValueInput.createByReal(params['cs_dia'] / 10.0)
            cs_angle = adsk.core.ValueInput.createByString(f"{params['cs_angle']} deg")
            h_in = hole_feats.createCountersinkInput(h_dia, cs_dia, cs_angle)
        else:
            h_in = hole_feats.createSimpleInput(h_dia)
        
        # Position and depth
        pt = adsk.core.Point3D.create(params['x'], params['y'], 0)
        h_in.setPositionByPoint(face, pt)
        
        if params.get('through_all', False):
            h_in.setAllExtent()
        else:
            h_in.setDistanceExtent(adsk.core.ValueInput.createByReal(params['depth'] / 10.0))
            
        # Threaded (Tapped) support
        if params.get('is_threaded', False):
            t_type = params.get('thread_type', 'ISO Metric profile')
            t_desig = params['thread_desig']
            t_class = params.get('thread_class', '6H')
            t_data = hole_feats.createThreadData(True, t_type, t_desig, t_class)
            h_in.tapSettings = adsk.fusion.HoleTapSettings.TappedHoleTapSettings
            h_in.threadData = t_data
            
        # Tip type
        if params.get('is_flat', True):
            h_in.tipAngle = adsk.core.ValueInput.createByString("180 deg")
        
        hole_feat = hole_feats.add(h_in)
        returnValue.append("OK")
except Exception as e:
    returnValue.append(f"ERR_API:{str(e)}")"""


def build_create_pattern_on_path_script() -> str:
    return """try:
    target = find_body_recursive(root, params['body'])
    path_sk = find_sketch_recursive(root, params['path_sketch'])
    
    if target and path_sk and path_sk.sketchCurves.count > 0:
        ents = adsk.core.ObjectCollection.create()
        ents.add(target)
        
        # Use first curve as path
        path = active_comp.features.createPath(path_sk.sketchCurves.item(0))
        patterns = active_comp.features.pathPatternFeatures
        quantity = adsk.core.ValueInput.createByReal(params['count'])
        distance = adsk.core.ValueInput.createByReal(params['dist'])
        
        p_in = patterns.createInput(ents, path, quantity, distance, adsk.fusion.PatternDistanceType.ExtentPatternDistanceType)
        p_in.isSymmetric = params.get('symmetric', False)
        patterns.add(p_in)
        returnValue.append("OK")
    else: returnValue.append("ERR_INPUT")
except Exception as e:
    returnValue.append(f"ERR_API:{str(e)}")"""


def build_mirror_features_script() -> str:
    return """try:
    target_feat = None
    for f in active_comp.features:
        if f.name == params['feature_name']:
            target_feat = f
            break
            
    plane = {"XY": active_comp.xYConstructionPlane, "XZ": active_comp.xZConstructionPlane, "YZ": active_comp.yZConstructionPlane}.get(params['plane'], active_comp.xYConstructionPlane)
    
    if target_feat:
        ents = adsk.core.ObjectCollection.create()
        ents.add(target_feat)
        mirrors = active_comp.features.mirrorFeatures
        m_in = mirrors.createInput(ents, plane)
        mirrors.add(m_in)
        returnValue.append("OK")
    else: returnValue.append("ERR_FEATURE")
except Exception as e:
    returnValue.append(f"ERR_API:{str(e)}")"""


def build_delete_face_script() -> str:
    return """try:
    target = find_body_recursive(root, params['body'])
    if target:
        face_idx = params.get('face_index', 0)
        if face_idx < target.faces.count:
            face = target.faces.item(face_idx)
            delete_feats = target.parentComponent.features.surfaceDeleteFaceFeatures
            delete_feats.add(face)
            returnValue.append("OK")
        else: returnValue.append("ERR_FACE_INDEX")
    else: returnValue.append("ERR_BODY")
except Exception as e:
    returnValue.append(f"ERR_API:{str(e)}")"""


def build_offset_face_script() -> str:
    return """try:
    target = find_body_recursive(root, params['body'])
    if target:
        face_idx = params.get('face_index', 0)
        if face_idx < target.faces.count:
            face = target.faces.item(face_idx)
            faces = adsk.core.ObjectCollection.create()
            faces.add(face)
            offsets = target.parentComponent.features.offsetFeatures
            dist = adsk.core.ValueInput.createByReal(params['dist'])
            o_in = offsets.createInput(faces, dist, adsk.fusion.FeatureOperations.NewBodyFeatureOperation, False)
            offsets.add(o_in)
            returnValue.append("OK")
        else: returnValue.append("ERR_FACE_INDEX")
    else: returnValue.append("ERR_BODY")
except Exception as e:
    returnValue.append(f"ERR_API:{str(e)}")"""


def build_move_face_script() -> str:
    return """try:
    target = find_body_recursive(root, params['body'])
    if target:
        face_idx = params.get('face_index', 0)
        if face_idx < target.faces.count:
            face = target.faces.item(face_idx)
            ents = adsk.core.ObjectCollection.create()
            ents.add(face)
            moves = target.parentComponent.features.moveFeatures
            trans = adsk.core.Matrix3D.create()
            trans.translation = adsk.core.Vector3D.create(params['x'], params['y'], params['z'])
            m_in = moves.createInput(ents, trans)
            moves.add(m_in)
            returnValue.append("OK")
        else: returnValue.append("ERR_FACE_INDEX")
    else: returnValue.append("ERR_BODY")
except Exception as e:
    returnValue.append(f"ERR_API:{str(e)}")"""


def build_combine_bodies_script() -> str:
    return """try:
    target, owner_comp, target_err = resolve_body_context(
        params['target'],
        params.get('component_name'),
        params.get('component_path')
    )
    tools = adsk.core.ObjectCollection.create()
    owner_mismatch = False
    for name in params['tool_bodies']:
        t, tool_owner, tool_err = resolve_body_context(
            name,
            params.get('component_name'),
            params.get('component_path')
        )
        if t and tool_owner == owner_comp:
            tools.add(t)
        elif t:
            owner_mismatch = True

    if target_err == "ERR_COMPONENT":
        returnValue.append("ERR_COMPONENT")
    elif owner_mismatch:
        returnValue.append("ERR_OWNER_MISMATCH")
    elif target and tools.count > 0:
        combines = owner_comp.features.combineFeatures
        c_in = combines.createInput(target, tools)
        op = params.get('operation', 'Join').lower()
        if op == 'cut': c_in.operation = adsk.fusion.FeatureOperations.CutFeatureOperation
        elif op == 'intersect': c_in.operation = adsk.fusion.FeatureOperations.IntersectFeatureOperation
        else: c_in.operation = adsk.fusion.FeatureOperations.JoinFeatureOperation
        
        try:
            combines.add(c_in)
            returnValue.append("OK")
        except:
            returnValue.append("ERR_COMBINE_FAILED_GEOMETRY")
    else: returnValue.append("ERR_NOT_FOUND")
except Exception as e:
    returnValue.append(f"ERR_API:{str(e)}")"""


def build_move_body_absolute_script() -> str:
    return """try:
    target = find_body_recursive(root, params['body'])
    if target:
        ents = adsk.core.ObjectCollection.create(); ents.add(target)
        current_center = target.physicalProperties.centerOfMass
        
        dx = params['x'] - current_center.x
        dy = params['y'] - current_center.y
        dz = params['z'] - current_center.z
        
        moves = active_comp.features.moveFeatures
        transform = adsk.core.Matrix3D.create()
        transform.translation = adsk.core.Vector3D.create(dx, dy, dz)
        
        m_in = moves.createInput(ents, transform)
        moves.add(m_in)
        returnValue.append("OK")
    else: returnValue.append("ERR_NOT_FOUND")
except Exception as e:
    returnValue.append(f"ERR_API:{str(e)}")"""


def build_delete_body_script() -> str:
    return """try:
    target = find_body_recursive(root, params['body'])
    if target:
        target.deleteMe()
        returnValue.append("OK")
    else: returnValue.append("ERR_NOT_FOUND")
except Exception as e:
    returnValue.append(f"ERR_API:{str(e)}")"""


def build_rename_body_script() -> str:
    return """try:
    target = find_body_recursive(root, params['old_name'])
    if target:
        target.name = params['new_name']
        returnValue.append(target.name)
    else: returnValue.append("ERR_NOT_FOUND")
except Exception as e:
    returnValue.append(f"ERR_API:{str(e)}")"""


def build_split_body_script() -> str:
    return """try:
    target, owner_comp, target_err = resolve_body_context(
        params['body'],
        params.get('component_name'),
        params.get('component_path')
    )
    if target_err == "ERR_COMPONENT":
        returnValue.append("ERR_COMPONENT")
    elif not target:
        returnValue.append("ERR_BODY")
    else:
        owner = owner_comp
        tool_name = str(params.get('tool', '')).strip().upper()
        tool = {
            "XY": owner.xYConstructionPlane,
            "XZ": owner.xZConstructionPlane,
            "YZ": owner.yZConstructionPlane
        }.get(tool_name)
        if not tool:
            tool, tool_owner, tool_err = resolve_body_context(
                params['tool'],
                params.get('component_name'),
                params.get('component_path')
            )
            if tool and tool_owner != owner:
                returnValue.append("ERR_OWNER_MISMATCH")
                tool = None

        if len(returnValue) > 0:
            pass
        elif target and tool:
            splits = owner.features.splitBodyFeatures
            s_in = splits.createInput(target, tool, True)
            splits.add(s_in)
            returnValue.append("OK")
        elif target:
            returnValue.append("ERR_TOOL")
        else:
            bodies = [b.name for b in root.bRepBodies]
            returnValue.append(f"ERR_BODY (Available: {bodies})")
except Exception as e:
    returnValue.append(f"ERR_API:{str(e)}")"""


def build_scale_body_script() -> str:
    return """try:
    target = find_body_recursive(root, params['body'])
    if target:
        ents = adsk.core.ObjectCollection.create(); ents.add(target)
        scales = active_comp.features.scaleFeatures
        origin = root.originConstructionPoint
        factor = adsk.core.ValueInput.createByReal(params['factor'])
        s_in = scales.createInput(ents, origin, factor)
        scales.add(s_in)
        returnValue.append("OK")
    else: returnValue.append("ERR_NOT_FOUND")
except Exception as e:
    returnValue.append(f"ERR_API:{str(e)}")"""


def build_move_body_script() -> str:
    return """try:
    target = find_body_recursive(root, params['body'])
    if target:
        ents = adsk.core.ObjectCollection.create(); ents.add(target)
        moves = active_comp.features.moveFeatures
        transform = adsk.core.Matrix3D.create()
        vector = adsk.core.Vector3D.create(params['x'], params['y'], params['z'])
        transform.translation = vector
        if params.get('angle', 0) != 0:
            rot_mat = adsk.core.Matrix3D.create()
            rot_mat.setToRotation(params['angle'] * (3.14159/180.0), active_comp.zConstructionAxis, root.originConstructionPoint)
            transform.transformBy(rot_mat)
            
        m_in = moves.createInput(ents, transform)
        moves.add(m_in)
        returnValue.append("OK")
    else: returnValue.append("ERR_NOT_FOUND")
except Exception as e:
    returnValue.append(f"ERR_API:{str(e)}")"""


def build_create_plastic_rib_script() -> str:
    return """try:
    path_sk = find_sketch_recursive(root, params['path_sketch'])
    if path_sk and path_sk.sketchCurves.count > 0:
        line = path_sk.sketchCurves.item(0)
        ribs = active_comp.features.ribFeatures
        r_in = ribs.createInput(line, True)
        r_in.thickness = adsk.core.ValueInput.createByReal(params['thick'])
        r_in.extentType = adsk.fusion.RibExtentTypes.ToNextRibExtentType
        rib_feat = ribs.add(r_in)
        returnValue.append(rib_feat.name)
    else: returnValue.append("ERR_PATH")
except Exception as e:
    returnValue.append(f"ERR_API:{str(e)}")"""


def build_create_plastic_web_script() -> str:
    return """try:
    path_sk = find_sketch_recursive(root, params['path_sketch'])
    if path_sk and path_sk.sketchCurves.count > 0:
        curves = adsk.core.ObjectCollection.create()
        for i in range(path_sk.sketchCurves.count):
            curves.add(path_sk.sketchCurves.item(i))
        webs = active_comp.features.webFeatures
        w_in = webs.createInput(curves, True)
        w_in.thickness = adsk.core.ValueInput.createByReal(params['thick'])
        w_in.depthOptions.setDepthToNext()
        web_feat = webs.add(w_in)
        returnValue.append(web_feat.name)
    else: returnValue.append("ERR_PATH")
except Exception as e:
    returnValue.append(f"ERR_API:{str(e)}")"""


def build_create_plastic_boss_script() -> str:
    return """try:
    path_sk = find_sketch_recursive(root, params['path_sketch'])
    if path_sk and path_sk.sketchPoints.count > 0:
        pts = adsk.core.ObjectCollection.create()
        for i in range(path_sk.sketchPoints.count):
            pts.add(path_sk.sketchPoints.item(i))

        owner = path_sk.parentComponent if path_sk.parentComponent else root
        if not hasattr(owner.features, 'bossFeatures'):
            returnValue.append("ERR_UNSUPPORTED")
        else:
            bosses = owner.features.bossFeatures
            b_in = bosses.createInput()
            b_in.setPositionBySketchPoints(pts)

            side = b_in.createSideInput()
            side.isEnabled = True
            side.setSimple(adsk.core.ValueInput.createByReal(0.8), adsk.core.ValueInput.createByReal(0.4))
            
            if params.get('is_thread', True):
                b_in.side2 = side
            else:
                b_in.side1 = side

            try:
                boss_feat = bosses.add(b_in)
                returnValue.append(boss_feat.name)
            except Exception as e:
                if "Design Extension" in str(e):
                    returnValue.append("ERR_EXTENSION")
                else:
                    returnValue.append(f"ERR_API_ADD:{str(e)}")
    else:
        returnValue.append("ERR_SKETCH")
except Exception as e:
    returnValue.append(f"ERR_API:{str(e)}")"""


def build_create_snap_fit_script() -> str:
    return """try:
    path_sk = find_sketch_recursive(root, params['path_sketch'])
    if path_sk and path_sk.sketchPoints.count > 0:
        owner = path_sk.parentComponent if path_sk.parentComponent else root
        if not hasattr(owner.features, 'snapFitFeatures'):
            returnValue.append("ERR_UNSUPPORTED")
        else:
            snaps = owner.features.snapFitFeatures
            pt = path_sk.sketchPoints.item(0)
            sel = adsk.core.ObjectCollection.create()
            sel.add(pt)
            
            s_in = snaps.createInput(sel, adsk.fusion.SnapFitType.ParallelHookAndGrooveSnapFitType)
            if root.bRepBodies.count >= 1:
                s_in.hookBody = root.bRepBodies.item(0)
            if root.bRepBodies.count >= 2:
                s_in.grooveBody = root.bRepBodies.item(1)
                
            snap_feat = snaps.add(s_in)
            returnValue.append(snap_feat.name)
    else: returnValue.append("ERR_POINT")
except Exception as e:
    returnValue.append(f"ERR_API:{str(e)}")"""


def build_create_cylinder_script() -> str:
    return """try:
    plane = {"XY": active_comp.xYConstructionPlane, "XZ": active_comp.xZConstructionPlane, "YZ": active_comp.yZConstructionPlane}.get(params['plane'], active_comp.xYConstructionPlane)
    center = adsk.core.Point3D.create(params['x'], params['y'], params['z'])
    sk = active_comp.sketches.add(plane)
    sk.sketchCurves.sketchCircles.addByCenterRadius(center, params['r'])
    prof = sk.profiles.item(0)
    ext = active_comp.features.extrudeFeatures.addSimple(prof, adsk.core.ValueInput.createByReal(params['h']), adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    body = ext.bodies.item(0)
    body.name = params['name']
    if body.parentComponent != active_comp:
        try: body.moveToComponent(d.activeOccurrence)
        except: pass
    if find_body_recursive(root, body.name):
        returnValue.append(body.name)
    else:
        returnValue.append("ERR_VERIFICATION_FAILED")
except Exception as e:
    returnValue.append(f"ERR_API:{str(e)}")"""


def build_create_sphere_script() -> str:
    return """try:
    center = adsk.core.Point3D.create(params['x'], params['y'], params['z'])
    radius = params['r']
    sk = active_comp.sketches.add(active_comp.xYConstructionPlane)
    
    startPoint = adsk.core.Point3D.create(center.x, center.y + radius, center.z)
    endPoint = adsk.core.Point3D.create(center.x, center.y - radius, center.z)
    alongArcPoint = adsk.core.Point3D.create(center.x + radius, center.y, center.z)
    
    arc = sk.sketchCurves.sketchArcs.addByThreePoints(startPoint, alongArcPoint, endPoint)
    axisLine = sk.sketchCurves.sketchLines.addByTwoPoints(startPoint, endPoint)
    
    if sk.profiles.count > 0:
        prof = sk.profiles.item(0)
        revolves = active_comp.features.revolveFeatures
        rev_in = revolves.createInput(prof, axisLine, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
        rev_in.isSolid = False
        angle = adsk.core.ValueInput.createByReal(2 * math.pi)
        rev_in.setAngleExtent(False, angle)
        rev_feat = revolves.add(rev_in)
        body = rev_feat.bodies.item(0)
        body.name = params['name']
        if find_body_recursive(root, body.name):
            returnValue.append(body.name)
        else:
            returnValue.append("ERR_VERIFICATION_FAILED")
    else:
        returnValue.append("ERR_SKETCH")
except Exception as e:
    returnValue.append(f"ERR_API:{str(e)}")"""


def build_create_torus_script() -> str:
    return """try:
    center = adsk.core.Point3D.create(params['x'], params['y'], params['z'])
    major_r = params['major_r']
    minor_r = params['minor_r']
    
    sk = active_comp.sketches.add(active_comp.xYConstructionPlane)
    circle_center = adsk.core.Point3D.create(center.x + major_r, center.y, center.z)
    sk.sketchCurves.sketchCircles.addByCenterRadius(circle_center, minor_r)
    
    axis_start = adsk.core.Point3D.create(center.x, center.y, center.z)
    axis_end = adsk.core.Point3D.create(center.x, center.y, center.z + 1.0)
    axisLine = sk.sketchCurves.sketchLines.addByTwoPoints(axis_start, axis_end)
    
    if sk.profiles.count > 0:
        prof = sk.profiles.item(0)
        revolves = active_comp.features.revolveFeatures
        rev_in = revolves.createInput(prof, axisLine, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
        rev_in.isSolid = False
        angle = adsk.core.ValueInput.createByReal(2 * math.pi)
        rev_in.setAngleExtent(False, angle)
        rev_feat = revolves.add(rev_in)
        body = rev_feat.bodies.item(0)
        body.name = params['name']
        if find_body_recursive(root, body.name):
            returnValue.append(body.name)
        else:
            returnValue.append("ERR_VERIFICATION_FAILED")
    else:
        returnValue.append("ERR_SKETCH")
except Exception as e:
    returnValue.append(f"ERR_API:{str(e)}")"""


def build_create_coil_script() -> str:
    return """try:
    before_tokens = set()
    for i in range(active_comp.bRepBodies.count):
        before_tokens.add(active_comp.bRepBodies.item(i).entityToken)

    app.executeTextCommand(u'Commands.Start PrimitiveCoil')
    app.executeTextCommand(u'NuCommands.CommitCmd')

    created = None
    for i in range(active_comp.bRepBodies.count):
        body = active_comp.bRepBodies.item(i)
        if body.entityToken not in before_tokens:
            created = body
            break

    if created:
        created.name = params['name']
        if find_body_recursive(root, created.name):
            returnValue.append(created.name)
        else:
            returnValue.append("ERR_VERIFICATION_FAILED")
    else:
        returnValue.append("ERR_UNSUPPORTED: Coil creation is not available in the current Fusion command/runtime context.")
except Exception as e:
    returnValue.append(f"ERR_API:{str(e)}")"""


def build_create_pipe_script() -> str:
    return """try:
    path_sk = find_sketch_recursive(root, params['path_sketch'])
    if path_sk and path_sk.sketchCurves.count > 0:
        path = active_comp.features.createPath(path_sk.sketchCurves.item(0))
        pipes = active_comp.features.pipeFeatures
        p_in = pipes.createInput(path, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
        p_in.sectionShape = adsk.fusion.PipeSectionShapeTypes.CircularPipeSectionShapeType
        p_in.distance = adsk.core.ValueInput.createByReal(1.0)
        p_in.sectionThickness = adsk.core.ValueInput.createByReal(params['thickness'])
        pipe_feat = pipes.add(p_in)
        body = pipe_feat.bodies.item(0)
        body.name = params['name']
        if find_body_recursive(root, body.name):
            returnValue.append(body.name)
        else:
            returnValue.append("ERR_VERIFICATION_FAILED")
    else: returnValue.append("ERR_PATH")
except Exception as e:
    returnValue.append(f"ERR_API:{str(e)}")"""


def build_create_box_script() -> str:
    return """try:
    pt = adsk.core.Point3D.create(0, 0, 0)
    s = active_comp.sketches.add(active_comp.xYConstructionPlane)
    s.sketchCurves.sketchLines.addTwoPointRectangle(
        pt, adsk.core.Point3D.create(pt.x + params['l'], pt.y + params['w'], 0)
    )
    if s.profiles.count < 1:
        returnValue.append("ERR_NO_PROFILE")
    else:
        prof = s.profiles.item(0)
        box = active_comp.features.extrudeFeatures.addSimple(
            prof,
            adsk.core.ValueInput.createByReal(params['h']),
            adsk.fusion.FeatureOperations.NewBodyFeatureOperation
        )
        body = box.bodies.item(0)
        translate_body(body, params['x'], params['y'], params['z'])
        body.name = params['name']
        if find_body_recursive(root, body.name):
            returnValue.append(body.name)
        else:
            returnValue.append("ERR_VERIFICATION_FAILED")
except Exception as e:
    returnValue.append(f"ERR_API:{str(e)}")"""


def build_create_circular_pattern_script() -> str:
    return """try:
    target = find_body_recursive(root, params['body'])
    if target:
        ents = adsk.core.ObjectCollection.create()
        ents.add(target)
        axis = {"X": active_comp.xConstructionAxis, "Y": active_comp.yConstructionAxis, "Z": active_comp.zConstructionAxis}.get(params['axis'], active_comp.zConstructionAxis)
        patterns = active_comp.features.circularPatternFeatures
        p_in = patterns.createInput(ents, axis)
        p_in.quantity = adsk.core.ValueInput.createByReal(params['count'])
        p_in.totalAngle = adsk.core.ValueInput.createByString("360 deg")
        patterns.add(p_in)
        returnValue.append("OK")
    else: returnValue.append("ERR_BODY")
except Exception as e:
    returnValue.append(f"ERR_API:{str(e)}")"""


def build_create_rectangular_pattern_script() -> str:
    return """try:
    target = find_body_recursive(root, params['body'])
    if target:
        ents = adsk.core.ObjectCollection.create()
        ents.add(target)
        patterns = active_comp.features.rectangularPatternFeatures
        p_in = patterns.createInput(ents, active_comp.xConstructionAxis, adsk.core.ValueInput.createByReal(params['cx']), adsk.core.ValueInput.createByReal(params['dx']), adsk.fusion.RectangularPatternSpacingTypes.SpacingRectangularPatternSpacingType)
        if params['cy'] > 1:
            p_in.directionTwo = active_comp.yConstructionAxis
            p_in.quantityTwo = adsk.core.ValueInput.createByReal(params['cy'])
            p_in.distanceTwo = adsk.core.ValueInput.createByReal(params['dy'])
        patterns.add(p_in)
        returnValue.append("OK")
    else: returnValue.append("ERR_BODY")
except Exception as e:
    returnValue.append(f"ERR_API:{str(e)}")"""


def build_create_fillet_script() -> str:
    return """try:
    target = find_body_recursive(root, params['body'])
    if target:
        edges = adsk.core.ObjectCollection.create()
        for e in target.edges: edges.add(e)
        fillets = target.parentComponent.features.filletFeatures
        f_in = fillets.createInput()
        f_in.addConstantRadiusEdgeSet(edges, adsk.core.ValueInput.createByReal(params['r']), True)
        fillets.add(f_in)
        returnValue.append("OK")
    else: returnValue.append("ERR_BODY")
except Exception as e:
    returnValue.append(f"ERR_API:{str(e)}")"""


def build_create_edge_fillet_script() -> str:
    return """try:
    target = find_body_recursive(root, params['body'])
    if target:
        fillets = active_comp.features.filletFeatures
        edge_col = adsk.core.ObjectCollection.create()
        for edge in target.edges: edge_col.add(edge)
        f_in = fillets.createInput()
        f_in.addConstantRadiusEdgeSet(edge_col, adsk.core.ValueInput.createByReal(params['r']), True)
        fillets.add(f_in)
        returnValue.append("OK")
    else: returnValue.append("ERR_BODY")
except Exception as e:
    returnValue.append(f"ERR_API:{str(e)}")"""


def build_extrude_sketch_script() -> str:
    return """try:
    def ensure_unique_body_name(owner_comp, desired_name):
        base_name = str(desired_name or 'Body').strip() or 'Body'
        candidate = base_name
        suffix = 2
        while find_body_recursive(root, candidate):
            candidate = f"{base_name}_{suffix}"
            suffix += 1
        return candidate

    def pick_body_name(payload, fallback_prefix, source_name=None):
        requested = str(payload.get('name', '') or '').strip()
        if requested and requested.lower() not in ('body', 'body1', 'body2', 'body3', 'newbody'):
            return requested
        source = str(source_name or '').strip().replace(' ', '_')
        if source:
            if source.lower().endswith('sketch'):
                source = source[:-6].rstrip('_') or source
            return f"{source}_{fallback_prefix}"
        return fallback_prefix

    s, owner_comp, err = resolve_sketch_context(
        params['sketch'],
        params.get('component_name'),
        params.get('component_path')
    )
    if err == "ERR_COMPONENT":
        returnValue.append("ERR_COMPONENT")
    elif not s:
        returnValue.append("ERR_SKETCH")
    else:
        owner_comp = activate_component_context(owner_comp)
        # Determine which profiles to extrude
        idx = params.get('profile_index')
        profs = adsk.core.ObjectCollection.create()
        
        if idx is not None and 0 <= idx < s.profiles.count:
            profs.add(s.profiles.item(idx))
        else:
            # Add all standard profiles
            for p in s.profiles:
                profs.add(p)
            # Add all sketch texts (they don't count as standard profiles but can be extruded)
            for t in s.sketchTexts:
                profs.add(t)
        
        if profs.count > 0:
            # Determine operation
            op_str = params.get('op', 'NewBody')
            ops = {
                'Join': adsk.fusion.FeatureOperations.JoinFeatureOperation,
                'Cut': adsk.fusion.FeatureOperations.CutFeatureOperation,
                'Intersect': adsk.fusion.FeatureOperations.IntersectFeatureOperation,
                'NewBody': adsk.fusion.FeatureOperations.NewBodyFeatureOperation,
                'NewComponent': adsk.fusion.FeatureOperations.NewComponentFeatureOperation
            }
            op = ops.get(op_str, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
            
            extrudes = owner_comp.features.extrudeFeatures
            ext_in = extrudes.createInput(profs, op)
            
            # Support for start offset
            offset_val = params.get('offset', 0)
            if offset_val != 0:
                offset = adsk.fusion.OffsetStartDefinition.create(adsk.core.ValueInput.createByReal(offset_val))
                ext_in.startExtent = offset
                
            ext_in.setDistanceExtent(False, adsk.core.ValueInput.createByReal(params['dist']))
            
            # Targeted body selection for Cut/Join
            target_body_name = params.get('target_body')
            if target_body_name:
                target_body, target_owner, target_err = resolve_body_context(
                    target_body_name,
                    params.get('component_name'),
                    params.get('component_path')
                )
                if target_err == "ERR_COMPONENT":
                    returnValue.append("ERR_COMPONENT")
                elif target_body and target_owner == owner_comp:
                    ext_in.participantBodies = [target_body]
                elif target_body:
                    returnValue.append("ERR_OWNER_MISMATCH")
                else:
                    returnValue.append("ERR_TARGET_BODY")
            elif op in [adsk.fusion.FeatureOperations.CutFeatureOperation, adsk.fusion.FeatureOperations.JoinFeatureOperation]:
                # Fallback: Include all bodies in the sketch owner component.
                all_bodies = collect_component_bodies(owner_comp)
                if all_bodies:
                    ext_in.participantBodies = all_bodies
            if len(returnValue) == 0:
                ext = extrudes.add(ext_in)

                if op == adsk.fusion.FeatureOperations.NewBodyFeatureOperation and ext.bodies.count > 0:
                    ext.bodies.item(0).name = ensure_unique_body_name(owner_comp, pick_body_name(params, 'Extrude', params.get('sketch')))
                    created_name = ext.bodies.item(0).name
                    if find_body_recursive(root, created_name):
                        returnValue.append(created_name)
                    else:
                        returnValue.append("ERR_VERIFICATION_FAILED")
                elif op == adsk.fusion.FeatureOperations.NewComponentFeatureOperation and ext.bodies.count > 0:
                    created_name = ext.bodies.item(0).name
                    if find_body_recursive(root, created_name):
                        returnValue.append(created_name)
                    else:
                        returnValue.append("ERR_VERIFICATION_FAILED")
                elif ext.bodies.count > 0:
                    returnValue.append(ext.bodies.item(0).name)
                else:
                    returnValue.append("OK")
        else:
            returnValue.append("ERR_NO_PROFILE")
except Exception as e:
    returnValue.append(f"ERR_API:{str(e)}")"""


def build_get_feature_history_script() -> str:
    return """try:
    history = []
    # Wir listen alle Features der aktiven Komponente in chronologischer Reihenfolge
    for f in active_comp.features:
        history.append({
            "name": f.name,
            "type": f.objectType.split('::')[-1],
            "is_suppressed": f.isSuppressed,
            "health": str(f.healthState)
        })
    import json
    returnValue.append(json.dumps(history))
except Exception as e:
    returnValue.append(f"ERR_API:{str(e)}")"""


def build_delete_feature_script() -> str:
    return """try:
    target_name = params['feature_name']
    feature = None
    for f in active_comp.features:
        if f.name == target_name:
            feature = f
            break
    
    if feature:
        feature.deleteMe()
        returnValue.append("OK")
    else:
        returnValue.append("ERR_NOT_FOUND")
except Exception as e:
    returnValue.append(f"ERR_API:{str(e)}")"""


def build_edit_feature_script() -> str:
    return """try:
    target_name = params.get('feature_name')
    feature = None
    for f in active_comp.features:
        if f.name == target_name:
            feature = f
            break
            
    if feature:
        # 1. Namen ändern
        if 'new_name' in params and params['new_name'] is not None:
            try: feature.name = str(params['new_name'])
            except: pass
            
        # 2. Unterdrückung (Suppression)
        if 'suppress' in params and params['suppress'] is not None:
            try: feature.isSuppressed = bool(params['suppress'])
            except: pass
            
        # 3. Parameter-Update
        if 'value' in params and params['value'] is not None:
            try:
                if hasattr(feature, 'extentDefinition'):
                    feature.extentDefinition.distance.expression = str(params['value'])
            except: pass
            
        returnValue.append("OK")
    else:
        returnValue.append("ERR_NOT_FOUND")
except Exception as e:
    returnValue.append(f"ERR_API:{str(e)}")"""


def build_create_hole_script() -> str:
    return """try:
    plane = get_offset_plane(active_comp.xYConstructionPlane, params['z'])
    sketch = active_comp.sketches.add(plane)
    center = adsk.core.Point3D.create(params['x'], params['y'], 0)
    sketch.sketchCurves.sketchCircles.addByCenterRadius(center, params['d'] / 20.0)
    if sketch.profiles.count < 1:
        returnValue.append("ERR_NO_PROFILE")
    else:
        extrudes = active_comp.features.extrudeFeatures
        ext_in = extrudes.createInput(sketch.profiles.item(0), adsk.fusion.FeatureOperations.CutFeatureOperation)
        ext_in.setDistanceExtent(False, adsk.core.ValueInput.createByReal(1000.0))
        extrudes.add(ext_in)
        returnValue.append("OK")
except Exception as e:
    returnValue.append(f"ERR_API:{str(e)}")"""


def build_create_sweep_advanced_script() -> str:
    return build_create_sweep_script()

def build_apply_3d_features_script() -> str:
    return """
try:
    results = []
    ops = params.get('operations', [])

    def ensure_unique_body_name(owner_comp, desired_name):
        base_name = str(desired_name or 'Body').strip() or 'Body'
        candidate = base_name
        suffix = 2
        while find_body_recursive(root, candidate):
            candidate = f"{base_name}_{suffix}"
            suffix += 1
        return candidate

    def pick_body_name(op, fallback_prefix, source_name=None):
        requested = str(op.get('name', '') or '').strip()
        if requested and requested.lower() not in ('body', 'body1', 'body2', 'body3', 'newbody'):
            return requested
        source = str(source_name or '').strip()
        if source:
            source = source.replace(' ', '_')
            if source.lower().endswith('sketch'):
                source = source[:-6].rstrip('_') or source
            return f"{source}_{fallback_prefix}"
        return fallback_prefix

    def collect_body_refs(component, sink):
        comp_path = get_component_path(component)
        for body in component.bRepBodies:
            sink.append({
                'name': body.name,
                'component_path': comp_path,
                'label': f"{body.name} @ {comp_path}"
            })
        for occ in component.occurrences:
            collect_body_refs(occ.component, sink)

    def body_lookup_error(target_name, component_name=None, component_path=None):
        candidates = []
        scope = resolve_lookup_scope(component_name, component_path)
        if scope:
            collect_body_refs(scope, candidates)
        if (component_name or component_path) and scope != root:
            collect_body_refs(root, candidates)
        if not candidates:
            return f"ERR_BODY_NOT_FOUND (requested='{target_name}')"

        wanted = normalize_name(target_name)
        folded = ascii_fold_name(target_name)
        suggestions = []
        seen = set()
        for candidate in candidates:
            dedupe_key = (candidate['name'], candidate['component_path'])
            if dedupe_key in seen:
                continue
            seen.add(dedupe_key)
            candidate_norm = normalize_name(candidate['name'])
            candidate_folded = ascii_fold_name(candidate['name'])
            if wanted in candidate_norm or candidate_norm in wanted or folded in candidate_folded or candidate_folded in folded:
                suggestions.append(candidate['label'])
        if not suggestions:
            suggestions = [candidate['label'] for candidate in candidates[:5]]
        else:
            suggestions = suggestions[:5]
        return f"ERR_BODY_NOT_FOUND (requested='{target_name}'; suggestions={' | '.join(suggestions)})"

    def iter_named_features(component):
        collections = (
            component.features.extrudeFeatures,
            component.features.revolveFeatures,
            component.features.sweepFeatures,
            component.features.holeFeatures,
            component.features.filletFeatures,
            component.features.chamferFeatures,
            component.features.shellFeatures,
            component.features.combineFeatures,
            component.features.splitBodyFeatures,
            component.features.moveFeatures,
            component.features.scaleFeatures,
            component.features.offsetFeatures,
        )
        for collection in collections:
            try:
                for feature in collection:
                    yield feature
            except:
                pass

    def find_named_feature(feature_name, component_name=None, component_path=None):
        target_component = resolve_component_context(component_name, component_path)
        components = [target_component] if target_component else [root]
        if target_component and target_component != root:
            components.append(root)
        for component in components:
            for feature in iter_named_features(component):
                if getattr(feature, 'name', None) == feature_name:
                    return feature, component
        return None, None

    def body_in_requested_scope(body, component_name=None, component_path=None):
        if not body:
            return False
        if not (component_name or component_path):
            return True
        requested_component = resolve_component_context(component_name, component_path)
        if not requested_component:
            return False
        owner = get_owner_component(body)
        return owner == requested_component
    
    for op in ops:
        action = op.get('action') or op.get('type')
        try:
            if action == 'extrude':
                s, owner_comp, err = resolve_sketch_context(op['sketch'], op.get('component_name'), op.get('component_path'))
                if not s: results.append(f"{action}:ERR_SKETCH"); continue
                owner_comp = activate_component_context(owner_comp)
                profs = adsk.core.ObjectCollection.create()
                idx = op.get('profile_index')
                if idx is not None and 0 <= idx < s.profiles.count: profs.add(s.profiles.item(idx))
                else: [profs.add(p) for p in s.profiles]; [profs.add(t) for t in s.sketchTexts]
                if profs.count == 0: results.append(f"{action}:ERR_NO_PROFILE"); continue
                op_type = {'Join': 0, 'Cut': 1, 'Intersect': 2, 'NewBody': 3, 'NewComponent': 4}.get(op.get('op', 'NewBody'), 3)
                exts = owner_comp.features.extrudeFeatures
                ext_in = exts.createInput(profs, op_type)
                ext_in.setDistanceExtent(False, adsk.core.ValueInput.createByReal(op['dist']))
                ext_feat = exts.add(ext_in)
                if ext_feat.bodies.count > 0:
                    if op_type in (3, 4):
                        body = ext_feat.bodies.item(0)
                        body.name = ensure_unique_body_name(owner_comp, pick_body_name(op, 'Extrude', op.get('sketch')))
                    results.append(f"{action}:OK")
                else:
                    results.append(f"{action}:ERR_VERIFICATION_FAILED")
            elif action == 'create_loft':
                sketches, owner_comp, err = resolve_multi_sketch_context(op['sketch_names'], op.get('component_name'), op.get('component_path'))
                if not sketches or len(sketches) < 2: results.append(f"{action}:ERR_MIN_PROFILES"); continue
                owner_comp = activate_component_context(owner_comp)
                lofts = owner_comp.features.loftFeatures
                op_type = {'Join': 0, 'Cut': 1, 'Intersect': 2, 'NewBody': 3, 'NewComponent': 4}.get(op.get('op', 'NewBody'), 3)
                loft_in = lofts.createInput(op_type)
                for sk in sketches:
                    if sk.profiles.count > 0: loft_in.loftSections.add(sk.profiles.item(0))
                if 'centerline_sketch' in op:
                    cl_sk, _, _ = resolve_sketch_context(op['centerline_sketch'], op.get('component_name'), op.get('component_path'))
                    if cl_sk and cl_sk.sketchCurves.count > 0:
                        loft_in.centerLineOrRails.addCenterLine(
                            owner_comp.features.createPath(cl_sk.sketchCurves.item(0))
                        )
                loft_feat = lofts.add(loft_in)
                if loft_feat.bodies.count > 0 and op_type in (3, 4):
                    loft_feat.bodies.item(0).name = ensure_unique_body_name(owner_comp, pick_body_name(op, 'Loft', sketches[0].name))
                results.append(f"{action}:OK")
            elif action == 'create_sweep':
                prof_sk, owner_comp, p_err = resolve_sketch_context(op['profile_sketch'], op.get('component_name'), op.get('component_path'))
                path_sk, _, path_err = resolve_sketch_context(op['path_sketch'], op.get('component_name'), op.get('component_path'))
                if not prof_sk or not path_sk: results.append(f"{action}:ERR_INPUT_NOT_FOUND"); continue
                owner_comp = activate_component_context(owner_comp)
                sweeps = owner_comp.features.sweepFeatures
                prof = prof_sk.profiles.item(0)
                path = owner_comp.features.createPath(path_sk.sketchCurves.item(0))
                op_type = {'Join': 0, 'Cut': 1, 'Intersect': 2, 'NewBody': 3, 'NewComponent': 4}.get(op.get('op', 'NewBody'), 3)
                sweep_in = sweeps.createInput(prof, path, op_type)
                sweep_in.taperAngle = adsk.core.ValueInput.createByReal(op.get('taper', 0))
                sweep_in.twistAngle = adsk.core.ValueInput.createByReal(op.get('twist', 0))
                sweep_feat = sweeps.add(sweep_in)
                if sweep_feat.bodies.count > 0 and op_type in (3, 4):
                    sweep_feat.bodies.item(0).name = ensure_unique_body_name(owner_comp, pick_body_name(op, 'Sweep', prof_sk.name))
                results.append(f"{action}:OK")
            elif action == 'create_revolve':
                prof_sk, owner_comp, p_err = resolve_sketch_context(op['profile_sketch'], op.get('component_name'), op.get('component_path'))
                if not prof_sk: results.append(f"{action}:ERR_INPUT_NOT_FOUND"); continue
                owner_comp = activate_component_context(owner_comp)
                axis_entity = None
                if 'axis_sketch' in op:
                    ax_sk, _, _ = resolve_sketch_context(op['axis_sketch'], op.get('component_name'), op.get('component_path'))
                    if ax_sk and ax_sk.sketchCurves.sketchLines.count > 0: axis_entity = ax_sk.sketchCurves.sketchLines.item(0)
                if not axis_entity:
                    ax_name = op.get('axis', 'z').lower()
                    axis_entity = owner_comp.xConstructionAxis if ax_name == 'x' else owner_comp.yConstructionAxis if ax_name == 'y' else owner_comp.zConstructionAxis
                angle = adsk.core.ValueInput.createByReal(op.get('angle', 6.283185))
                revolves = owner_comp.features.revolveFeatures
                op_type = {'Join': 0, 'Cut': 1, 'Intersect': 2, 'NewBody': 3, 'NewComponent': 4}.get(op.get('op', 'NewBody'), 3)
                rev_in = revolves.createInput(prof_sk.profiles.item(0), axis_entity, op_type)
                rev_in.setAngleExtent(False, angle)
                rev_feat = revolves.add(rev_in)
                if rev_feat.bodies.count > 0 and op_type in (3, 4):
                    rev_feat.bodies.item(0).name = ensure_unique_body_name(owner_comp, pick_body_name(op, 'Revolve', prof_sk.name))
                results.append(f"{action}:OK")
            elif action == 'create_hole':
                target, owner_comp, target_err = resolve_body_context(op['body'], op.get('component_name'), op.get('component_path'))
                if not target or not owner_comp or not body_in_requested_scope(target, op.get('component_name'), op.get('component_path')):
                    results.append(f"{action}:{body_lookup_error(op['body'], op.get('component_name'), op.get('component_path'))}")
                    continue
                owner_comp = activate_component_context(owner_comp)
                face_index = op.get('face_index')
                if face_index is None:
                    planar_face = next((f for f in target.faces if f.geometry.surfaceType == adsk.core.SurfaceTypes.PlaneSurfaceType), None)
                    face = planar_face if planar_face else (target.faces.item(0) if target.faces.count > 0 else None)
                else:
                    face_index = int(face_index)
                    if face_index < 0 or face_index >= target.faces.count:
                        results.append(f"{action}:ERR_FACE_INDEX")
                        continue
                    face = target.faces.item(face_index)
                if not face:
                    results.append(f"{action}:ERR_FACE_INDEX")
                    continue

                hole_feats = owner_comp.features.holeFeatures
                h_type = str(op.get('hole_type', 'simple')).lower()
                h_dia = adsk.core.ValueInput.createByReal(float(op.get('dia', op.get('diameter'))))

                if h_type == 'counterbore':
                    cb_dia = adsk.core.ValueInput.createByReal(float(op['cb_dia']))
                    cb_depth = adsk.core.ValueInput.createByReal(float(op['cb_depth']))
                    h_in = hole_feats.createCounterboreInput(h_dia, cb_dia, cb_depth)
                elif h_type == 'countersink':
                    cs_dia = adsk.core.ValueInput.createByReal(float(op['cs_dia']))
                    cs_angle = adsk.core.ValueInput.createByReal(float(op.get('cs_angle', 1.570796)))
                    h_in = hole_feats.createCountersinkInput(h_dia, cs_dia, cs_angle)
                else:
                    h_in = hole_feats.createSimpleInput(h_dia)

                h_in.setPositionByPoint(face, adsk.core.Point3D.create(float(op.get('x', 0)), float(op.get('y', 0)), 0))
                if bool(op.get('through_all', False)):
                    h_in.setAllExtent()
                else:
                    h_in.setDistanceExtent(adsk.core.ValueInput.createByReal(float(op['depth'])))
                if bool(op.get('is_flat', False)):
                    h_in.tipAngle = adsk.core.ValueInput.createByString("180 deg")
                hole_feats.add(h_in)
                results.append(f"{action}:OK")
            elif action == 'draft':
                target, owner_comp, target_err = resolve_body_context(op['body'], op.get('component_name'), op.get('component_path'))
                if not target or not owner_comp or not body_in_requested_scope(target, op.get('component_name'), op.get('component_path')):
                    results.append(f"{action}:{body_lookup_error(op['body'], op.get('component_name'), op.get('component_path'))}")
                    continue
                owner_comp = activate_component_context(owner_comp)
                face_index = int(op.get('face_index', 0))
                if face_index < 0 or face_index >= target.faces.count:
                    results.append(f"{action}:ERR_FACE_INDEX")
                    continue
                pull_plane_name = str(op.get('pull_plane', 'XY')).upper()
                pull_plane = {
                    'XY': owner_comp.xYConstructionPlane,
                    'XZ': owner_comp.xZConstructionPlane,
                    'YZ': owner_comp.yZConstructionPlane,
                }.get(pull_plane_name)
                if not pull_plane:
                    results.append(f"{action}:ERR_TOOL")
                    continue
                faces = [target.faces.item(face_index)]
                draft_input = owner_comp.features.draftFeatures.createInput(
                    faces,
                    pull_plane,
                    bool(op.get('is_tangent_chain', True))
                )
                draft_input.setSingleAngle(bool(op.get('is_symmetric', False)), adsk.core.ValueInput.createByReal(float(op['angle'])))
                if op.get('flip_direction') is not None:
                    draft_input.isDirectionFlipped = bool(op.get('flip_direction'))
                owner_comp.features.draftFeatures.add(draft_input)
                results.append(f"{action}:OK")
            elif action == 'circular_pattern':
                target, owner_comp, target_err = resolve_body_context(op['body'], op.get('component_name'), op.get('component_path'))
                if not target or not owner_comp or not body_in_requested_scope(target, op.get('component_name'), op.get('component_path')):
                    results.append(f"{action}:{body_lookup_error(op['body'], op.get('component_name'), op.get('component_path'))}")
                    continue
                owner_comp = activate_component_context(owner_comp)
                ents = adsk.core.ObjectCollection.create()
                ents.add(target)
                axis_name = str(op.get('axis', 'Z')).upper()
                axis = {'X': owner_comp.xConstructionAxis, 'Y': owner_comp.yConstructionAxis, 'Z': owner_comp.zConstructionAxis}.get(axis_name, owner_comp.zConstructionAxis)
                patterns = owner_comp.features.circularPatternFeatures
                p_in = patterns.createInput(ents, axis)
                p_in.quantity = adsk.core.ValueInput.createByReal(float(op['count']))
                p_in.totalAngle = adsk.core.ValueInput.createByReal(float(op.get('total_angle', 6.283185)))
                patterns.add(p_in)
                results.append(f"{action}:OK")
            elif action == 'rectangular_pattern':
                target, owner_comp, target_err = resolve_body_context(op['body'], op.get('component_name'), op.get('component_path'))
                if not target or not owner_comp or not body_in_requested_scope(target, op.get('component_name'), op.get('component_path')):
                    results.append(f"{action}:{body_lookup_error(op['body'], op.get('component_name'), op.get('component_path'))}")
                    continue
                owner_comp = activate_component_context(owner_comp)
                ents = adsk.core.ObjectCollection.create()
                ents.add(target)
                axis_one_name = str(op.get('axis_one', 'X')).upper()
                axis_two_name = str(op.get('axis_two', 'Y')).upper()
                axis_map = {'X': owner_comp.xConstructionAxis, 'Y': owner_comp.yConstructionAxis, 'Z': owner_comp.zConstructionAxis}
                patterns = owner_comp.features.rectangularPatternFeatures
                p_in = patterns.createInput(
                    ents,
                    axis_map.get(axis_one_name, owner_comp.xConstructionAxis),
                    adsk.core.ValueInput.createByReal(float(op['count_x'])),
                    adsk.core.ValueInput.createByReal(float(op['dist_x'])),
                    adsk.fusion.PatternDistanceType.SpacingPatternDistanceType
                )
                count_y = int(op.get('count_y', 1))
                if count_y > 1:
                    p_in.setDirectionTwo(
                        axis_map.get(axis_two_name, owner_comp.yConstructionAxis),
                        adsk.core.ValueInput.createByReal(count_y),
                        adsk.core.ValueInput.createByReal(float(op.get('dist_y', 0)))
                    )
                patterns.add(p_in)
                results.append(f"{action}:OK")
            elif action == 'path_pattern':
                target, owner_comp, target_err = resolve_body_context(op['body'], op.get('component_name'), op.get('component_path'))
                if not target or not owner_comp or not body_in_requested_scope(target, op.get('component_name'), op.get('component_path')):
                    results.append(f"{action}:{body_lookup_error(op['body'], op.get('component_name'), op.get('component_path'))}")
                    continue
                path_sk, path_owner, path_err = resolve_sketch_context(op['path_sketch'], op.get('component_name'), op.get('component_path'))
                if not path_sk or path_sk.sketchCurves.count < 1:
                    results.append(f"{action}:ERR_SKETCH")
                    continue
                if path_owner != owner_comp:
                    results.append(f"{action}:ERR_OWNER_MISMATCH")
                    continue
                owner_comp = activate_component_context(owner_comp)
                ents = adsk.core.ObjectCollection.create()
                ents.add(target)
                path = owner_comp.features.createPath(path_sk.sketchCurves.item(0))
                patterns = owner_comp.features.pathPatternFeatures
                p_in = patterns.createInput(
                    ents,
                    path,
                    adsk.core.ValueInput.createByReal(float(op['count'])),
                    adsk.core.ValueInput.createByReal(float(op['dist'])),
                    adsk.fusion.PatternDistanceType.ExtentPatternDistanceType
                )
                if op.get('is_symmetric') is not None:
                    p_in.isSymmetric = bool(op.get('is_symmetric'))
                patterns.add(p_in)
                results.append(f"{action}:OK")

            elif action == 'fillet':
                target = find_body_recursive(root, op['body'])
                if not target: results.append(f"{action}:ERR_BODY"); continue
                edges = adsk.core.ObjectCollection.create()
                for e in target.edges: edges.add(e)
                fillets = target.parentComponent.features.filletFeatures
                f_in = fillets.createInput()
                f_in.addConstantRadiusEdgeSet(edges, adsk.core.ValueInput.createByReal(op['r']), True)
                fillets.add(f_in)
                results.append(f"{action}:OK")

            elif action == 'chamfer':
                target = find_body_recursive(root, op['body'])
                if not target: results.append(f"{action}:ERR_BODY"); continue
                edges = adsk.core.ObjectCollection.create()
                for e in target.edges: edges.add(e)
                chamfers = target.parentComponent.features.chamferFeatures
                c_in = chamfers.createInput(edges, True)
                c_in.setToEqualDistance(adsk.core.ValueInput.createByReal(op['dist']))
                chamfers.add(c_in)
                results.append(f"{action}:OK")

            elif action == 'combine':
                target, owner_comp, target_err = resolve_body_context(op['target'], op.get('component_name'), op.get('component_path'))
                if not target: results.append(f"{action}:ERR_TARGET"); continue
                tools = adsk.core.ObjectCollection.create()
                for name in op['tool_bodies']:
                    t, _, _ = resolve_body_context(name, op.get('component_name'), op.get('component_path'))
                    if t: tools.add(t)
                combines = owner_comp.features.combineFeatures
                c_in = combines.createInput(target, tools)
                c_in.operation = {'cut': 1, 'intersect': 2}.get(op.get('operation', 'join').lower(), 0)
                combines.add(c_in)
                results.append(f"{action}:OK")

            elif action == 'create_box' or action == 'Box':
                target_comp = get_default_target_component(op)
                if not target_comp: results.append(f"{action}:ERR_COMPONENT"); continue
                pt = adsk.core.Point3D.create(0, 0, 0)
                s = target_comp.sketches.add(target_comp.xYConstructionPlane)
                s.sketchCurves.sketchLines.addTwoPointRectangle(pt, adsk.core.Point3D.create(pt.x + op['l'], pt.y + op['w'], 0))
                if s.profiles.count > 0:
                    h = float(op.get('height', op.get('h', 0)))
                    box = target_comp.features.extrudeFeatures.addSimple(s.profiles.item(0), adsk.core.ValueInput.createByReal(h), 3)
                    body = box.bodies.item(0)
                    translate_body(body, op.get('x', 0), op.get('y', 0), op.get('z', 0))
                    body.name = ensure_unique_body_name(target_comp, pick_body_name(op, 'Box'))
                    if find_body_recursive(target_comp, body.name):
                        results.append(f"{action}:OK:{body.name}")
                    else:
                        results.append(f"{action}:ERR_VERIFICATION_FAILED")
                else: results.append(f"{action}:ERR_NO_PROFILE")

            elif action == 'create_cylinder' or action == 'Cylinder':
                target_comp = get_default_target_component(op)
                if not target_comp: results.append(f"{action}:ERR_COMPONENT"); continue
                center_coords = op.get('center', [0,0,0])
                center = adsk.core.Point3D.create(op.get('x', center_coords[0]), op.get('y', center_coords[1]), op.get('z', center_coords[2]))
                sk = target_comp.sketches.add(target_comp.xYConstructionPlane)
                r = float(op.get('radius', op.get('r', 0)))
                h = float(op.get('height', op.get('h', 0)))
                sk.sketchCurves.sketchCircles.addByCenterRadius(center, r)
                ext = target_comp.features.extrudeFeatures.addSimple(sk.profiles.item(0), adsk.core.ValueInput.createByReal(h), 3)
                body = ext.bodies.item(0); body.name = ensure_unique_body_name(target_comp, pick_body_name(op, 'Cylinder'))
                if find_body_recursive(target_comp, body.name):
                    results.append(f"{action}:OK:{body.name}")
                else:
                    results.append(f"{action}:ERR_VERIFICATION_FAILED")

            elif action == 'create_sphere' or action == 'Sphere':
                target_comp = get_default_target_component(op)
                if not target_comp: results.append(f"{action}:ERR_COMPONENT"); continue
                center_coords = op.get('center', [0,0,0])
                center = adsk.core.Point3D.create(op.get('x', center_coords[0]), op.get('y', center_coords[1]), op.get('z', center_coords[2]))
                r = float(op.get('radius', op.get('r', 0.1)))
                sk = target_comp.sketches.add(target_comp.xYConstructionPlane)
                startPoint = adsk.core.Point3D.create(center.x, center.y + r, center.z)
                endPoint = adsk.core.Point3D.create(center.x, center.y - r, center.z)
                alongArcPoint = adsk.core.Point3D.create(center.x + r, center.y, center.z)
                sk.sketchCurves.sketchArcs.addByThreePoints(startPoint, alongArcPoint, endPoint)
                axisLine = sk.sketchCurves.sketchLines.addByTwoPoints(startPoint, endPoint)
                if sk.profiles.count > 0:
                    rev_in = target_comp.features.revolveFeatures.createInput(sk.profiles.item(0), axisLine, 3)
                    rev_in.isSolid = True
                    rev_in.setAngleExtent(False, adsk.core.ValueInput.createByReal(2 * 3.14159))
                    rev_feat = target_comp.features.revolveFeatures.add(rev_in)
                    body = rev_feat.bodies.item(0); body.name = ensure_unique_body_name(target_comp, pick_body_name(op, 'Sphere'))
                    if find_body_recursive(target_comp, body.name):
                        results.append(f"{action}:OK:{body.name}")
                    else:
                        results.append(f"{action}:ERR_VERIFICATION_FAILED")
                else:
                    results.append(f"{action}:ERR_NO_PROFILE")

            elif action == 'delete_body':
                target, owner_comp, target_err = resolve_body_context(op['body'], op.get('component_name'), op.get('component_path'))
                if not target or not body_in_requested_scope(target, op.get('component_name'), op.get('component_path')):
                    results.append(f"{action}:{body_lookup_error(op['body'], op.get('component_name'), op.get('component_path'))}")
                    continue
                
                # Activate owner component to ensure deletion works
                owner_comp = activate_component_context(owner_comp)
                
                target_name = target.name
                deleted = target.deleteMe()
                if not deleted:
                    results.append(f"{action}:ERR_DELETE_FAILED")
                else:
                    results.append(f"{action}:OK")

            elif action == 'rename_body':
                target, owner_comp, target_err = resolve_body_context(op['body'], op.get('component_name'), op.get('component_path'))
                if not target or not body_in_requested_scope(target, op.get('component_name'), op.get('component_path')):
                    results.append(f"{action}:{body_lookup_error(op['body'], op.get('component_name'), op.get('component_path'))}")
                    continue
                new_name = op.get('new_name')
                if not new_name:
                    results.append(f"{action}:ERR_NEW_NAME_REQUIRED")
                else:
                    target.name = str(new_name)
                    results.append(f"{action}:OK:{target.name}")

            elif action == 'move_body':
                target, owner_comp, target_err = resolve_body_context(op['body'], op.get('component_name'), op.get('component_path'))
                if not target or not owner_comp or not body_in_requested_scope(target, op.get('component_name'), op.get('component_path')):
                    results.append(f"{action}:{body_lookup_error(op['body'], op.get('component_name'), op.get('component_path'))}")
                    continue
                ents = adsk.core.ObjectCollection.create()
                ents.add(target)
                transform = adsk.core.Matrix3D.create()
                if any(k in op for k in ['x', 'y', 'z']):
                    transform.translation = adsk.core.Vector3D.create(op.get('x', 0), op.get('y', 0), op.get('z', 0))
                
                # Add rotation support
                if any(k in op for k in ['rx', 'ry', 'rz']):
                    if op.get('rx'):
                        rot = adsk.core.Matrix3D.create()
                        rot.setToRotation(op['rx'], adsk.core.Vector3D.create(1,0,0), target.physicalProperties.centerOfMass)
                        transform.transformBy(rot)
                    if op.get('ry'):
                        rot = adsk.core.Matrix3D.create()
                        rot.setToRotation(op['ry'], adsk.core.Vector3D.create(0,1,0), target.physicalProperties.centerOfMass)
                        transform.transformBy(rot)
                    if op.get('rz'):
                        rot = adsk.core.Matrix3D.create()
                        rot.setToRotation(op['rz'], adsk.core.Vector3D.create(0,0,1), target.physicalProperties.centerOfMass)
                        transform.transformBy(rot)

                moves = owner_comp.features.moveFeatures
                move_input = moves.createInput(ents, transform)
                moves.add(move_input)
                results.append(f"{action}:OK")

            elif action == 'move_body_absolute':
                target, owner_comp, target_err = resolve_body_context(op['body'], op.get('component_name'), op.get('component_path'))
                if not target or not owner_comp or not body_in_requested_scope(target, op.get('component_name'), op.get('component_path')):
                    results.append(f"{action}:{body_lookup_error(op['body'], op.get('component_name'), op.get('component_path'))}")
                    continue
                ents = adsk.core.ObjectCollection.create()
                ents.add(target)
                current_center = target.physicalProperties.centerOfMass
                dx = op['x'] - current_center.x
                dy = op['y'] - current_center.y
                dz = op['z'] - current_center.z
                transform = adsk.core.Matrix3D.create()
                transform.translation = adsk.core.Vector3D.create(dx, dy, dz)

                # Add rotation support for absolute move (rotates around center after translation)
                if any(k in op for k in ['rx', 'ry', 'rz']):
                    target_pt = adsk.core.Point3D.create(op['x'], op['y'], op['z'])
                    if op.get('rx'):
                        rot = adsk.core.Matrix3D.create()
                        rot.setToRotation(op['rx'], adsk.core.Vector3D.create(1,0,0), target_pt)
                        transform.transformBy(rot)
                    if op.get('ry'):
                        rot = adsk.core.Matrix3D.create()
                        rot.setToRotation(op['ry'], adsk.core.Vector3D.create(0,1,0), target_pt)
                        transform.transformBy(rot)
                    if op.get('rz'):
                        rot = adsk.core.Matrix3D.create()
                        rot.setToRotation(op['rz'], adsk.core.Vector3D.create(0,0,1), target_pt)
                        transform.transformBy(rot)

                moves = owner_comp.features.moveFeatures
                move_input = moves.createInput(ents, transform)
                moves.add(move_input)
                results.append(f"{action}:OK")

            elif action == 'execute_python':
                # Dynamically execute script provided in operation
                script_code = op.get('script')
                if script_code:
                    exec_globals = {
                        'adsk': adsk, 
                        'app': app, 
                        'design': design, 
                        'root': root, 
                        'active_comp': active_comp,
                        'params': op.get('params', {}),
                        'returnValue': []
                    }
                    exec(script_code, exec_globals)
                    res_val = exec_globals.get('returnValue')
                    results.append(f"{action}:OK:{res_val[0] if res_val else ''}")
                else:
                    results.append(f"{action}:ERR_NO_SCRIPT")

            elif action == 'pattern_feature':
                feature, feature_owner = find_named_feature(op.get('feature_name'), op.get('component_name'), op.get('component_path'))
                if not feature:
                    results.append(f"{action}:ERR_FEATURE_NOT_FOUND")
                    continue
                ents = adsk.core.ObjectCollection.create()
                ents.add(feature)
                axis_name = str(op.get('axis', 'Z')).upper()
                axis = {'X': feature_owner.xConstructionAxis, 'Y': feature_owner.yConstructionAxis, 'Z': feature_owner.zConstructionAxis}.get(axis_name, feature_owner.zConstructionAxis)
                patterns = feature_owner.features.circularPatternFeatures
                p_in = patterns.createInput(ents, axis)
                p_in.quantity = adsk.core.ValueInput.createByReal(float(op['count']))
                p_in.totalAngle = adsk.core.ValueInput.createByReal(float(op.get('total_angle', 6.283185)))
                patterns.add(p_in)
                results.append(f"{action}:OK")

            elif action == 'rectangular_pattern_feature':
                feature, feature_owner = find_named_feature(op.get('feature_name'), op.get('component_name'), op.get('component_path'))
                if not feature:
                    results.append(f"{action}:ERR_FEATURE_NOT_FOUND")
                    continue
                ents = adsk.core.ObjectCollection.create()
                ents.add(feature)
                axis_one_name = str(op.get('axis_one', 'X')).upper()
                axis_two_name = str(op.get('axis_two', 'Y')).upper()
                axis_map = {'X': feature_owner.xConstructionAxis, 'Y': feature_owner.yConstructionAxis, 'Z': feature_owner.zConstructionAxis}
                patterns = feature_owner.features.rectangularPatternFeatures
                p_in = patterns.createInput(
                    ents,
                    axis_map.get(axis_one_name, feature_owner.xConstructionAxis),
                    adsk.core.ValueInput.createByReal(float(op['count_x'])),
                    adsk.core.ValueInput.createByReal(float(op['dist_x'])),
                    adsk.fusion.PatternDistanceType.SpacingPatternDistanceType
                )
                count_y = int(op.get('count_y', 1))
                if count_y > 1:
                    p_in.setDirectionTwo(
                        axis_map.get(axis_two_name, feature_owner.yConstructionAxis),
                        adsk.core.ValueInput.createByReal(count_y),
                        adsk.core.ValueInput.createByReal(float(op.get('dist_y', 0)))
                    )
                patterns.add(p_in)
                results.append(f"{action}:OK")

            elif action == 'mirror_feature':
                feature, feature_owner = find_named_feature(op.get('feature_name'), op.get('component_name'), op.get('component_path'))
                if not feature:
                    results.append(f"{action}:ERR_FEATURE_NOT_FOUND")
                    continue
                plane_name = str(op.get('plane', 'XY')).upper()
                mirror_plane = {
                    'XY': feature_owner.xYConstructionPlane,
                    'XZ': feature_owner.xZConstructionPlane,
                    'YZ': feature_owner.yZConstructionPlane,
                }.get(plane_name)
                if not mirror_plane:
                    results.append(f"{action}:ERR_TOOL")
                    continue
                ents = adsk.core.ObjectCollection.create()
                ents.add(feature)
                mirrors = feature_owner.features.mirrorFeatures
                m_in = mirrors.createInput(ents, mirror_plane)
                mirrors.add(m_in)
                results.append(f"{action}:OK")

            elif action == 'create_construction_plane':
                target_comp = get_default_target_component(op)
                if not target_comp: results.append(f"{action}:ERR_COMPONENT"); continue
                planes = target_comp.constructionPlanes
                plane_in = planes.createInput()
                plane_type = op.get('plane_type', 'offset')
                if plane_type == 'offset':
                    base_plane_name = str(op.get('base_plane', 'XY')).upper()
                    base_plane = {'XY': target_comp.xYConstructionPlane, 'XZ': target_comp.xZConstructionPlane, 'YZ': target_comp.yZConstructionPlane}.get(base_plane_name, target_comp.xYConstructionPlane)
                    plane_in.setByOffset(base_plane, adsk.core.ValueInput.createByReal(float(op.get('offset', 0))))
                elif plane_type == 'angle':
                    axis_name = str(op.get('axis', 'X')).upper()
                    axis = {'X': target_comp.xConstructionAxis, 'Y': target_comp.yConstructionAxis, 'Z': target_comp.zConstructionAxis}.get(axis_name, target_comp.xConstructionAxis)
                    plane_in.setByAngle(axis, adsk.core.ValueInput.createByReal(float(op.get('angle', 0))), target_comp.xYConstructionPlane) # PlanarEntity as ref
                planes.add(plane_in)
                results.append(f"{action}:OK")

            elif action == 'create_construction_axis':
                target_comp = get_default_target_component(op)
                if not target_comp: results.append(f"{action}:ERR_COMPONENT"); continue
                axes = target_comp.constructionAxes
                axis_in = axes.createInput()
                axis_type = op.get('axis_type', 'two_point')
                if axis_type == 'two_point':
                    pt1 = adsk.core.Point3D.create(op.get('x1',0), op.get('y1',0), op.get('z1',0))
                    pt2 = adsk.core.Point3D.create(op.get('x2',1), op.get('y2',1), op.get('z2',1))
                    sk = target_comp.sketches.add(target_comp.xYConstructionPlane)
                    pt1_sk = sk.sketchPoints.add(pt1)
                    pt2_sk = sk.sketchPoints.add(pt2)
                    axis_in.setByTwoPoints(pt1_sk, pt2_sk)
                elif axis_type == 'cylinder':
                    target, owner_comp, target_err = resolve_body_context(op['body'], op.get('component_name'), op.get('component_path'))
                    if not target: results.append(f"{action}:ERR_BODY"); continue
                    face_index = int(op.get('face_index', 0))
                    if face_index >= target.faces.count: results.append(f"{action}:ERR_FACE_INDEX"); continue
                    face = target.faces.item(face_index)
                    axis_in.setByCylinderOrCone(face)
                axes.add(axis_in)
                results.append(f"{action}:OK")

            elif action == 'create_thread':
                target, owner_comp, target_err = resolve_body_context(op['body'], op.get('component_name'), op.get('component_path'))
                if not target or not owner_comp: results.append(f"{action}:ERR_BODY"); continue
                face_index = int(op.get('face_index', 0))
                if face_index >= target.faces.count: results.append(f"{action}:ERR_FACE_INDEX"); continue
                face = target.faces.item(face_index)
                threads = owner_comp.features.threadFeatures
                thread_data = owner_comp.parentDesign.threadDataQuery
                thread_types = thread_data.allThreadTypes
                t_type = op.get('thread_type', thread_types[0])
                all_sizes = thread_data.allSizes(t_type)
                size = op.get('size', all_sizes[0])
                all_designations = thread_data.allDesignations(t_type, size)
                designation = op.get('designation', all_designations[0])
                all_classes = thread_data.allClasses(False, t_type, designation)
                t_class = op.get('thread_class', all_classes[0])
                t_info = threads.createThreadInfo(False, t_type, designation, t_class)
                faces = adsk.core.ObjectCollection.create()
                faces.add(face)
                t_in = threads.createInput(faces, t_info)
                t_in.isModeled = bool(op.get('is_modeled', False))
                threads.add(t_in)
                results.append(f"{action}:OK")

            elif action == 'create_coil':
                target_comp = get_default_target_component(op)
                if not target_comp: results.append(f"{action}:ERR_COMPONENT"); continue
                center_coords = op.get('center', [0,0,0])
                center = adsk.core.Point3D.create(op.get('x', center_coords[0]), op.get('y', center_coords[1]), op.get('z', center_coords[2]))
                coils = target_comp.features.coilFeatures
                c_in = coils.createInput(target_comp.xYConstructionPlane, center)
                c_in.diameter = adsk.core.ValueInput.createByReal(float(op.get('dia', 1.0)))
                c_in.height = adsk.core.ValueInput.createByReal(float(op.get('height', 5.0)))
                c_in.pitch = adsk.core.ValueInput.createByReal(float(op.get('pitch', 1.0)))
                c_in.isSolid = True
                c_in.operation = {'join': 0, 'cut': 1, 'intersect': 2, 'newbody': 3}.get(op.get('op', 'newbody').lower(), 3)
                coils.add(c_in)
                results.append(f"{action}:OK")

            elif action == 'select_by_property':
                target, owner_comp, target_err = resolve_body_context(op['body'], op.get('component_name'), op.get('component_path'))
                if not target: results.append(f"{action}:ERR_BODY"); continue
                prop = op.get('property', 'area')
                min_val = float(op.get('min_val', 0))
                max_val = float(op.get('max_val', 999999))
                indices = []
                if prop == 'area':
                    for i in range(target.faces.count):
                        if min_val <= target.faces.item(i).area <= max_val:
                            indices.append(i)
                elif prop == 'length':
                    for i in range(target.edges.count):
                        if min_val <= target.edges.item(i).length <= max_val:
                            indices.append(i)
                results.append(f"{action}:OK:{','.join(map(str, indices))}")

            elif action == 'align_to_normal':
                target, owner_comp, target_err = resolve_body_context(op['body'], op.get('component_name'), op.get('component_path'))
                target_face_body, _, _ = resolve_body_context(op['target_body'], op.get('component_name'), op.get('component_path'))
                if not target or not target_face_body: results.append(f"{action}:ERR_BODY"); continue
                face_index = int(op.get('face_index', 0))
                if face_index >= target_face_body.faces.count: results.append(f"{action}:ERR_FACE_INDEX"); continue
                face = target_face_body.faces.item(face_index)
                evaluator = face.evaluator
                _, normal = evaluator.getNormalAtPoint(face.pointOnFace)
                
                ents = adsk.core.ObjectCollection.create()
                ents.add(target)
                
                align_axis = op.get('align_axis', 'Z').upper()
                vec = adsk.core.Vector3D.create(1 if align_axis == 'X' else 0, 1 if align_axis == 'Y' else 0, 1 if align_axis == 'Z' else 0)
                
                angle = vec.angleTo(normal)
                axis = vec.crossProduct(normal)
                
                transform = adsk.core.Matrix3D.create()
                if axis.length > 0.001:
                    rot = adsk.core.Matrix3D.create()
                    rot.setToRotation(angle, axis, target.physicalProperties.centerOfMass)
                    transform.transformBy(rot)
                
                moves = owner_comp.features.moveFeatures
                move_input = moves.createInput(ents, transform)
                moves.add(move_input)
                results.append(f"{action}:OK")

            elif action == 'apply_taper_to_extrude':
                feature, feature_owner = find_named_feature(op.get('feature_name'), op.get('component_name'), op.get('component_path'))
                if not feature or feature.objectType != adsk.fusion.ExtrudeFeature.classType():
                    results.append(f"{action}:ERR_FEATURE_NOT_FOUND")
                    continue
                try:
                    feature.taperAngle = adsk.core.ValueInput.createByReal(float(op.get('taper', 0)))
                    results.append(f"{action}:OK")
                except:
                    results.append(f"{action}:ERR_API")

            elif action == 'scale_body':
                target, owner_comp, target_err = resolve_body_context(op['body'], op.get('component_name'), op.get('component_path'))
                if not target or not owner_comp or not body_in_requested_scope(target, op.get('component_name'), op.get('component_path')):
                    results.append(f"{action}:{body_lookup_error(op['body'], op.get('component_name'), op.get('component_path'))}")
                    continue
                ents = adsk.core.ObjectCollection.create()
                ents.add(target)
                scales = owner_comp.features.scaleFeatures
                origin = owner_comp.originConstructionPoint
                scale_input = scales.createInput(ents, origin, adsk.core.ValueInput.createByReal(op['factor']))
                scales.add(scale_input)
                results.append(f"{action}:OK")

            elif action == 'shell':
                target, owner_comp, target_err = resolve_body_context(op['body'], op.get('component_name'), op.get('component_path'))
                if not target or not owner_comp or not body_in_requested_scope(target, op.get('component_name'), op.get('component_path')):
                    results.append(f"{action}:{body_lookup_error(op['body'], op.get('component_name'), op.get('component_path'))}")
                    continue
                face_index = int(op.get('face_index', 0))
                if face_index < 0 or face_index >= target.faces.count:
                    results.append(f"{action}:ERR_FACE_INDEX")
                    continue
                face = target.faces.item(face_index)
                faces = adsk.core.ObjectCollection.create()
                faces.add(face)
                shell_input = owner_comp.features.shellFeatures.createInput(faces, False)
                shell_input.insideThickness = adsk.core.ValueInput.createByReal(op['thick'])
                owner_comp.features.shellFeatures.add(shell_input)
                results.append(f"{action}:OK")

            elif action == 'split_body':
                target, owner_comp, target_err = resolve_body_context(op['body'], op.get('component_name'), op.get('component_path'))
                if not target or not owner_comp or not body_in_requested_scope(target, op.get('component_name'), op.get('component_path')):
                    results.append(f"{action}:{body_lookup_error(op['body'], op.get('component_name'), op.get('component_path'))}")
                    continue
                tool_name = str(op.get('tool', '')).strip().upper()
                tool = {
                    'XY': owner_comp.xYConstructionPlane,
                    'XZ': owner_comp.xZConstructionPlane,
                    'YZ': owner_comp.yZConstructionPlane,
                }.get(tool_name)
                if not tool:
                    tool, tool_owner, tool_err = resolve_body_context(op.get('tool'), op.get('component_name'), op.get('component_path'))
                    if not tool:
                        results.append(f"{action}:ERR_TOOL")
                        continue
                    if tool_owner != owner_comp or not body_in_requested_scope(tool, op.get('component_name'), op.get('component_path')):
                        results.append(f"{action}:ERR_OWNER_MISMATCH")
                        continue
                split_input = owner_comp.features.splitBodyFeatures.createInput(target, tool, bool(op.get('extend', True)))
                owner_comp.features.splitBodyFeatures.add(split_input)
                results.append(f"{action}:OK")

            elif action == 'delete_face':
                target, owner_comp, target_err = resolve_body_context(op['body'], op.get('component_name'), op.get('component_path'))
                if not target or not owner_comp or not body_in_requested_scope(target, op.get('component_name'), op.get('component_path')):
                    results.append(f"{action}:{body_lookup_error(op['body'], op.get('component_name'), op.get('component_path'))}")
                    continue
                face_index = int(op.get('face_index', 0))
                if face_index < 0 or face_index >= target.faces.count:
                    results.append(f"{action}:ERR_FACE_INDEX")
                    continue
                owner_comp.features.surfaceDeleteFaceFeatures.add(target.faces.item(face_index))
                results.append(f"{action}:OK")

            elif action == 'offset_face':
                target, owner_comp, target_err = resolve_body_context(op['body'], op.get('component_name'), op.get('component_path'))
                if not target or not owner_comp or not body_in_requested_scope(target, op.get('component_name'), op.get('component_path')):
                    results.append(f"{action}:{body_lookup_error(op['body'], op.get('component_name'), op.get('component_path'))}")
                    continue
                face_index = int(op.get('face_index', 0))
                if face_index < 0 or face_index >= target.faces.count:
                    results.append(f"{action}:ERR_FACE_INDEX")
                    continue
                faces = adsk.core.ObjectCollection.create()
                faces.add(target.faces.item(face_index))
                offset_input = owner_comp.features.offsetFeatures.createInput(
                    faces,
                    adsk.core.ValueInput.createByReal(op['dist']),
                    adsk.fusion.FeatureOperations.NewBodyFeatureOperation,
                    False
                )
                owner_comp.features.offsetFeatures.add(offset_input)
                results.append(f"{action}:OK")

            elif action == 'move_face':
                target, owner_comp, target_err = resolve_body_context(op['body'], op.get('component_name'), op.get('component_path'))
                if not target or not owner_comp or not body_in_requested_scope(target, op.get('component_name'), op.get('component_path')):
                    results.append(f"{action}:{body_lookup_error(op['body'], op.get('component_name'), op.get('component_path'))}")
                    continue
                face_index = int(op.get('face_index', 0))
                if face_index < 0 or face_index >= target.faces.count:
                    results.append(f"{action}:ERR_FACE_INDEX")
                    continue
                ents = adsk.core.ObjectCollection.create()
                ents.add(target.faces.item(face_index))
                transform = adsk.core.Matrix3D.create()
                transform.translation = adsk.core.Vector3D.create(op.get('x', 0), op.get('y', 0), op.get('z', 0))
                move_input = owner_comp.features.moveFeatures.createInput(ents, transform)
                owner_comp.features.moveFeatures.add(move_input)
                results.append(f"{action}:OK")

            elif action == 'edit_feature':
                feature, feature_owner = find_named_feature(op.get('feature_name'), op.get('component_name'), op.get('component_path'))
                if not feature:
                    results.append(f"{action}:ERR_FEATURE_NOT_FOUND")
                    continue
                if op.get('new_name') is not None:
                    try:
                        feature.name = str(op.get('new_name'))
                    except:
                        pass
                if op.get('suppress') is not None:
                    try:
                        feature.isSuppressed = bool(op.get('suppress'))
                    except:
                        pass
                if op.get('value') is not None:
                    try:
                        if hasattr(feature, 'extentDefinition'):
                            feature.extentDefinition.distance.expression = str(op.get('value'))
                        elif hasattr(feature, 'distance'):
                            feature.distance.expression = str(op.get('value'))
                        else:
                            results.append(f"{action}:ERR_FEATURE_VALUE_UNSUPPORTED")
                            continue
                    except Exception as feature_err:
                        results.append(f"{action}:ERR:{str(feature_err)}")
                        continue
                results.append(f"{action}:OK")

            elif action == 'delete_feature':
                feature, feature_owner = find_named_feature(op.get('feature_name'), op.get('component_name'), op.get('component_path'))
                if not feature:
                    results.append(f"{action}:ERR_FEATURE_NOT_FOUND")
                    continue
                feature.deleteMe()
                results.append(f"{action}:OK")

            else:
                results.append(f"{action}:ERR_UNKNOWN_ACTION")

        except Exception as e:
            results.append(f"{action}:ERR:{str(e)}")
            
    returnValue.append(",".join(results) if results else "OK")
except Exception as e:
    returnValue.append(f"ERR_API:{str(e)}")
"""
