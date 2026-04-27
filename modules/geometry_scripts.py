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
    s = next((sk for sk in active_comp.sketches if sk.name == params['sketch']), None)
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
    path_sk = next((s for s in active_comp.sketches if s.name == params['path_sketch']), None)
    
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
    # This is more complex because we need the actual Feature objects, not bodies.
    # We attempt to find features by name in the timeline.
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
        # For simplicity, we delete the first face or a face at index if provided
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
    target = find_body_recursive(root, params['target'])
    tools = adsk.core.ObjectCollection.create()
    for name in params['tool_bodies']:
        t = find_body_recursive(root, name)
        if t: tools.add(t)
    
    if target and tools.count > 0:
        combines = target.parentComponent.features.combineFeatures
        c_in = combines.createInput(target, tools)
        op = params.get('operation', 'Join').lower()
        if op == 'cut': c_in.operation = adsk.fusion.FeatureOperations.CutFeatureOperation
        elif op == 'intersect': c_in.operation = adsk.fusion.FeatureOperations.IntersectFeatureOperation
        else: c_in.operation = adsk.fusion.FeatureOperations.JoinFeatureOperation
        
        try:
            combines.add(c_in)
            returnValue.append("OK")
        except:
            # Falls Combine fehlschlägt (oft wegen Berührung ohne Überlappung), 
            # geben wir einen Hinweis zurück, damit die KI neu positionieren kann.
            returnValue.append("ERR_COMBINE_FAILED_GEOMETRY")
    else: returnValue.append("ERR_NOT_FOUND")
except Exception as e:
    returnValue.append(f"ERR_API:{str(e)}")"""


def build_move_body_absolute_script() -> str:
    return """try:
    target = find_body_recursive(root, params['body'])
    if target:
        ents = adsk.core.ObjectCollection.create(); ents.add(target)
        # Aktueller Schwerpunkt
        current_center = target.physicalProperties.centerOfMass
        
        # Differenz berechnen
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


def build_split_body_script() -> str:
    return """try:
    target = find_body_recursive(root, params['body'])
    if not target:
        returnValue.append("ERR_BODY")
    else:
        owner = active_comp
        tool_name = str(params.get('tool', '')).strip().upper()
        tool = {
            "XY": owner.xYConstructionPlane,
            "XZ": owner.xZConstructionPlane,
            "YZ": owner.yZConstructionPlane
        }.get(tool_name)
        if not tool:
            tool = find_body_recursive(root, params['tool'])

        if target and tool:
            splits = owner.features.splitBodyFeatures
            s_in = splits.createInput(target, tool, True)
            splits.add(s_in)
            returnValue.append("OK")
        elif target:
            returnValue.append("ERR_TOOL")
        else:
            # Fallback for error message compatibility with geometry.py
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
        # Translation
        vector = adsk.core.Vector3D.create(params['x'], params['y'], params['z'])
        transform.translation = vector
        # Rotation (simplified: around Z axis if angle provided)
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
    path_sk = next((s for s in active_comp.sketches if s.name == params['path_sketch']), None)
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
    path_sk = next((s for s in active_comp.sketches if s.name == params['path_sketch']), None)
    if path_sk and path_sk.sketchCurves.count > 0:
        curves = adsk.core.ObjectCollection.create()
        for c in path_sk.sketchCurves: curves.add(c)
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

            # Create side input
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
            # Try to find target bodies for hook and groove
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
    returnValue.append(body.name)
except Exception as e:
    returnValue.append(f"ERR_API:{str(e)}")"""


def build_create_sphere_script() -> str:
    return """try:
    center = adsk.core.Point3D.create(params['x'], params['y'], params['z'])
    radius = params['r']
    sk = active_comp.sketches.add(active_comp.xYConstructionPlane)
    
    # Draw a semi-circle arc on the XY plane (vertical-ish)
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
        returnValue.append(body.name)
    else:
        returnValue.append("ERR_SKETCH")
except Exception as e:
    returnValue.append(f"ERR_API:{str(e)}")"""


def build_create_torus_script() -> str:
    return """try:
    center = adsk.core.Point3D.create(params['x'], params['y'], params['z'])
    major_r = params['major_r']
    minor_r = params['minor_r']
    
    # Create sketch on XY plane
    sk = active_comp.sketches.add(active_comp.xYConstructionPlane)
    
    # Draw circle for cross section, offset by major radius
    circle_center = adsk.core.Point3D.create(center.x + major_r, center.y, center.z)
    sk.sketchCurves.sketchCircles.addByCenterRadius(circle_center, minor_r)
    
    # Axis for revolution (Z axis through center)
    axis_start = adsk.core.Point3D.create(center.x, center.y, center.z)
    axis_end = adsk.core.Point3D.create(center.x, center.y, center.z + 1.0)
    # We can use construction axis or a line
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
        returnValue.append(body.name)
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
        returnValue.append(created.name)
    else:
        returnValue.append("ERR_UNSUPPORTED: Coil creation is not available in the current Fusion command/runtime context.")
except Exception as e:
    returnValue.append(f"ERR_API:{str(e)}")"""


def build_create_pipe_script() -> str:
    return """try:
    path_sk = next((s for s in active_comp.sketches if s.name == params['path_sketch']), None)
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
        returnValue.append(body.name)
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
        returnValue.append(body.name)
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


def build_extrude_sketch_script() -> str:
    return """try:
    s = next((sk for sk in active_comp.sketches if sk.name == params['sketch']), None)
    if s and s.profiles.count > 0:
        prof = s.profiles.item(0)
        extrudes = active_comp.features.extrudeFeatures
        ext_in = extrudes.createInput(prof, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
        ext_in.setDistanceExtent(False, adsk.core.ValueInput.createByReal(params['dist']))
        ext = extrudes.add(ext_in)
        returnValue.append(ext.bodies.item(0).name)
    else: returnValue.append("ERR_SKETCH")
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
