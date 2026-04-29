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
                    results.append(f"{action}:OK")
                else:
                    results.append(f"{action}:ERR_VERIFICATION_FAILED")

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
                    body.name = op.get('name', 'Box')
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
                body = ext.bodies.item(0); body.name = op.get('name', 'Cylinder')
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
                    body = rev_feat.bodies.item(0); body.name = op.get('name', 'Sphere')
                    if find_body_recursive(target_comp, body.name):
                        results.append(f"{action}:OK:{body.name}")
                    else:
                        results.append(f"{action}:ERR_VERIFICATION_FAILED")
                else:
                    results.append(f"{action}:ERR_NO_PROFILE")

            else:
                results.append(f"{action}:ERR_UNKNOWN_ACTION")

        except Exception as e:
            results.append(f"{action}:ERR:{str(e)}")
            
    returnValue.append(",".join(results) if results else "OK")
except Exception as e:
    returnValue.append(f"ERR_API:{str(e)}")
"""
