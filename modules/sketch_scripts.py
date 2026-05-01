import json

def build_create_sketch_script() -> str:
    return """try:
    owner_comp, target_plane, err = resolve_sketch_creation_context(params)
    if err:
        returnValue.append(err)
    elif target_plane:
        owner_comp = activate_component_context(owner_comp)
        # Create sketch in the owner component of the target geometry
        s = owner_comp.sketches.add(target_plane)
        s.name = params['name']
        if find_sketch_recursive(root, s.name):
            returnValue.append(s.name)
        else:
            returnValue.append("ERR_VERIFICATION_FAILED")
    else:
        returnValue.append("ERR_CONTEXT_NOT_RESOLVED")
except Exception as e:
    returnValue.append(f"ERR_API:{str(e)}")"""


def build_add_constraint_script() -> str:
    return """try:
    s, owner, err = resolve_sketch_context(params['sketch'])
    if err:
        returnValue.append(err)
    elif s:
        returnValue.append("OK")
    else: returnValue.append("ERR_SKETCH_NOT_FOUND")
except Exception as e:
    returnValue.append(f"ERR_API:{str(e)}")"""


def build_draw_line_script() -> str:
    return """try:
    s, owner, err = resolve_sketch_context(params['sketch'])
    if err:
        returnValue.append(err)
    elif s:
        p1 = adsk.core.Point3D.create(params['x1'], params['y1'], 0)
        p2 = adsk.core.Point3D.create(params['x2'], params['y2'], 0)
        line = s.sketchCurves.sketchLines.addByTwoPoints(p1, p2)
        returnValue.append("OK")
    else: returnValue.append("ERR_SKETCH_NOT_FOUND")
except Exception as e:
    returnValue.append(f"ERR_API:{str(e)}")"""


def build_draw_circle_script() -> str:
    return """try:
    s, owner, err = resolve_sketch_context(params['sketch'])
    if err:
        returnValue.append(err)
    elif s:
        center = adsk.core.Point3D.create(params['x'], params['y'], 0)
        s.sketchCurves.sketchCircles.addByCenterRadius(center, params['r'])
        returnValue.append("OK")
    else: returnValue.append("ERR_SKETCH_NOT_FOUND")
except Exception as e:
    returnValue.append(f"ERR_API:{str(e)}")"""


def build_draw_rectangle_script() -> str:
    return """try:
    s, owner, err = resolve_sketch_context(params['sketch'])
    if err:
        returnValue.append(err)
    elif s:
        p1 = adsk.core.Point3D.create(params['x1'], params['y1'], 0)
        p2 = adsk.core.Point3D.create(params['x2'], params['y2'], 0)
        s.sketchCurves.sketchLines.addTwoPointRectangle(p1, p2)
        returnValue.append("OK")
    else: returnValue.append("ERR_SKETCH_NOT_FOUND")
except Exception as e:
    returnValue.append(f"ERR_API:{str(e)}")"""


def build_sketch_circular_pattern_script() -> str:
    return """try:
    s, owner, err = resolve_sketch_context(params['sketch'])
    if err:
        returnValue.append(err)
    elif s:
        entities = []
        for curve_type in [s.sketchCurves.sketchLines, s.sketchCurves.sketchCircles, s.sketchCurves.sketchArcs, s.sketchCurves.sketchFittedSplines]:
            for c in curve_type: entities.append(c)
        
        if len(entities) < 1:
            returnValue.append("ERR_EMPTY")
        else:
            center_point = s.sketchPoints.add(adsk.core.Point3D.create(params['cx'], params['cy'], 0))
            constraints = s.geometricConstraints
            pattern_input = constraints.createCircularPatternInput(entities, center_point)
            pattern_input.quantity = adsk.core.ValueInput.createByReal(params['count'])
            pattern_input.totalAngle = adsk.core.ValueInput.createByString("360 deg")
            constraints.addCircularPattern(pattern_input)
            returnValue.append("OK")
    else: returnValue.append("ERR_SKETCH_NOT_FOUND")
except Exception as e:
    returnValue.append(f"ERR_API:{str(e)}")"""


def build_sketch_rectangular_pattern_script() -> str:
    return """try:
    s, owner, err = resolve_sketch_context(params['sketch'])
    if err:
        returnValue.append(err)
    elif s:
        entities = []
        for curve_type in [s.sketchCurves.sketchLines, s.sketchCurves.sketchCircles, s.sketchCurves.sketchArcs, s.sketchCurves.sketchFittedSplines]:
            for c in curve_type: entities.append(c)
            
        if len(entities) < 1:
            returnValue.append("ERR_EMPTY")
        else:
            constraints = s.geometricConstraints
            pattern_input = constraints.createRectangularPatternInput(entities, adsk.fusion.PatternDistanceType.SpacingPatternDistanceType)
            
            lines = s.sketchCurves.sketchLines
            dir1 = next((l for l in lines if l.isConstruction), None)
            if not dir1:
                dir1 = lines.addByTwoPoints(adsk.core.Point3D.create(0,0,0), adsk.core.Point3D.create(1,0,0))
                dir1.isConstruction = True
            
            pattern_input.setDirectionOne(dir1, adsk.core.ValueInput.createByReal(params['cx']), adsk.core.ValueInput.createByReal(params['dx']))
            
            if params['cy'] > 1:
                dir2 = next((l for l in lines if l.isConstruction and l != dir1), None)
                if not dir2:
                    dir2 = lines.addByTwoPoints(adsk.core.Point3D.create(0,0,0), adsk.core.Point3D.create(0,1,0))
                    dir2.isConstruction = True
                pattern_input.setDirectionTwo(dir2, adsk.core.ValueInput.createByReal(params['cy']), adsk.core.ValueInput.createByReal(params['dy']))
            
            constraints.addRectangularPattern(pattern_input)
            returnValue.append("OK")
    else: returnValue.append("ERR_SKETCH_NOT_FOUND")
except Exception as e:
    returnValue.append(f"ERR_API:{str(e)}")"""


def build_sketch_offset_script() -> str:
    return """try:
    s, owner, err = resolve_sketch_context(params['sketch'])
    if err:
        returnValue.append(err)
    elif s:
        entities = adsk.core.ObjectCollection.create()
        for curve_type in [s.sketchCurves.sketchLines, s.sketchCurves.sketchCircles, s.sketchCurves.sketchArcs, s.sketchCurves.sketchFittedSplines]:
            for c in curve_type: entities.add(c)
        if entities.count < 1:
            returnValue.append("ERR_EMPTY")
        else:
            offset_point = adsk.core.Point3D.create(10.0, 10.0, 0)
            s.offset(entities, offset_point, params['dist'])
            returnValue.append("OK")
    else: returnValue.append("ERR_SKETCH_NOT_FOUND")
except Exception as e:
    returnValue.append(f"ERR_API:{str(e)}")"""


def build_draw_arc_script() -> str:
    return """try:
    s, owner, err = resolve_sketch_context(params['sketch'])
    if err:
        returnValue.append(err)
    elif s:
        center = adsk.core.Point3D.create(params['cx'], params['cy'], 0)
        start = adsk.core.Point3D.create(params['sx'], params['sy'], 0)
        angle = (params['angle'] * 3.14159) / 180.0
        s.sketchCurves.sketchArcs.addByCenterStartSweep(center, start, angle)
        returnValue.append("OK")
    else: returnValue.append("ERR_SKETCH_NOT_FOUND")
except Exception as e:
    returnValue.append(f"ERR_API:{str(e)}")"""


def build_draw_polygon_script() -> str:
    return """try:
    import math
    s, owner, err = resolve_sketch_context(params['sketch'])
    if err:
        returnValue.append(err)
    elif s:
        center_x = float(params['cx'])
        center_y = float(params['cy'])
        r = float(params['r'])
        n = int(params['sides'])
        points = []
        for i in range(n):
            angle = i * (2.0 * math.pi / n)
            px = center_x + r * math.cos(angle)
            py = center_y + r * math.sin(angle)
            points.append(adsk.core.Point3D.create(px, py, 0))
        for i in range(n):
            s.sketchCurves.sketchLines.addByTwoPoints(points[i], points[(i+1) % n])
        returnValue.append("OK")
    else:
        returnValue.append("ERR_SKETCH_NOT_FOUND")
except Exception as e:
    returnValue.append(f"ERR_API:{str(e)}")"""


def build_draw_spline_script() -> str:
    return """try:
    s, owner, err = resolve_sketch_context(params['sketch'])
    if err:
        returnValue.append(err)
    elif s:
        points = adsk.core.ObjectCollection.create()
        for p in params['pts']: points.add(adsk.core.Point3D.create(p[0], p[1], 0))
        s.sketchCurves.sketchFittedSplines.add(points)
        returnValue.append("OK")
    else: returnValue.append("ERR_SKETCH_NOT_FOUND")
except Exception as e:
    returnValue.append(f"ERR_API:{str(e)}")"""


def build_sketch_project_script() -> str:
    return """try:
    s, s_owner, s_err = resolve_sketch_context(params['sketch'])
    target_body, b_owner, b_err = resolve_body_context(params['body'])
    
    if s_err: returnValue.append(s_err)
    elif b_err: returnValue.append(b_err)
    elif s and target_body:
        # Project edges
        for edge in target_body.edges:
            s.project(edge)
        returnValue.append("OK")
    else: returnValue.append("ERR_NOT_FOUND")
except Exception as e:
    returnValue.append(f"ERR_API:{str(e)}")"""


def build_draw_sketch_text_script() -> str:
    return """try:
    s, owner, err = resolve_sketch_context(params['sketch'])
    if err:
        returnValue.append(err)
    elif s:
        texts = s.sketchTexts
        point = adsk.core.Point3D.create(params['x'], params['y'], 0)
        t_input = texts.createInput(params['text'], params['height'], point)
        t_input.fontName = params.get('font', 'Arial')
        texts.add(t_input)
        returnValue.append("OK")
    else: returnValue.append("ERR_SKETCH_NOT_FOUND")
except Exception as e:
    returnValue.append(f"ERR_API:{str(e)}")"""


def build_draw_ellipse_script() -> str:
    return """try:
    s, owner, err = resolve_sketch_context(params['sketch'])
    if err:
        returnValue.append(err)
    elif s:
        center = adsk.core.Point3D.create(params['cx'], params['cy'], 0)
        major = adsk.core.Point3D.create(params['mx'], params['my'], 0)
        on_ellipse = adsk.core.Point3D.create(params['ox'], params['oy'], 0)
        s.sketchCurves.sketchEllipses.add(center, major, on_ellipse)
        returnValue.append("OK")
    else: returnValue.append("ERR_SKETCH_NOT_FOUND")
except Exception as e:
    returnValue.append(f"ERR_API:{str(e)}")"""


def build_sketch_mirror_script() -> str:
    return """try:
    s, owner, err = resolve_sketch_context(params['sketch'])
    if err:
        returnValue.append(err)
    elif s:
        returnValue.append("ERR_NOT_IMPLEMENTED_DYNAMICALLY")
    else: returnValue.append("ERR_SKETCH_NOT_FOUND")
except Exception as e:
    returnValue.append(f"ERR_API:{str(e)}")"""


def build_sketch_trim_script() -> str:
    return """try:
    s, owner, err = resolve_sketch_context(params['sketch'])
    if err:
        returnValue.append(err)
    elif s:
        returnValue.append("ERR_REQUIRES_SPECIFIC_CURVE")
    else: returnValue.append("ERR_SKETCH_NOT_FOUND")
except Exception as e:
    returnValue.append(f"ERR_API:{str(e)}")"""


def build_draw_slot_script() -> str:
    return """try:
    s, owner, err = resolve_sketch_context(params['sketch'])
    if err:
        returnValue.append(err)
    elif s:
        def add_center_to_center_slot(start_point, end_point, width_value):
            if hasattr(s, 'addCenterToCenterSlot'):
                s.addCenterToCenterSlot(start_point, end_point, width_value)
                return

            width_real = width_value.value if hasattr(width_value, 'value') else float(width_value)
            dx = end_point.x - start_point.x
            dy = end_point.y - start_point.y
            length = math.hypot(dx, dy)
            if length <= 1e-9:
                raise ValueError('slot length must be greater than zero')

            radius = width_real / 2.0
            ux = dx / length
            uy = dy / length
            px = -uy
            py = ux

            start_top = adsk.core.Point3D.create(start_point.x + (px * radius), start_point.y + (py * radius), 0)
            start_bottom = adsk.core.Point3D.create(start_point.x - (px * radius), start_point.y - (py * radius), 0)
            end_top = adsk.core.Point3D.create(end_point.x + (px * radius), end_point.y + (py * radius), 0)
            end_bottom = adsk.core.Point3D.create(end_point.x - (px * radius), end_point.y - (py * radius), 0)

            s.sketchCurves.sketchArcs.addByCenterStartSweep(start_point, start_top, math.pi)
            s.sketchCurves.sketchArcs.addByCenterStartSweep(end_point, end_bottom, math.pi)
            s.sketchCurves.sketchLines.addByTwoPoints(start_top, end_top)
            s.sketchCurves.sketchLines.addByTwoPoints(start_bottom, end_bottom)

        p1 = adsk.core.Point3D.create(params['x1'], params['y1'], 0)
        p2 = adsk.core.Point3D.create(params['x2'], params['y2'], 0)
        sw = adsk.core.ValueInput.createByReal(float(params['w']))
        add_center_to_center_slot(p1, p2, sw)
        returnValue.append("OK")
    else: returnValue.append("ERR_SKETCH_NOT_FOUND")
except Exception as e:
    returnValue.append(f"ERR_API:{str(e)}")"""


def build_edit_sketch_script() -> str:
    return """
import math
try:
    s, owner, err = resolve_sketch_context(params['sketch'], params.get('component_name'), params.get('component_path'))
    if err:
        returnValue.append(err)
    elif s:
        def editable_curves():
            curves = []
            for curve_group in (
                s.sketchCurves.sketchLines,
                s.sketchCurves.sketchCircles,
                s.sketchCurves.sketchArcs,
                s.sketchCurves.sketchEllipses,
                s.sketchCurves.sketchFittedSplines,
            ):
                for curve in curve_group:
                    curves.append(curve)
            return curves

        def get_primary_curve_index(op):
            idx = op.get('curve_index')
            if idx is None:
                curve_ref = op.get('curve_ref') or {}
                idx = curve_ref.get('curve_index')
            if idx is None:
                curve_indices = op.get('curve_indices')
                if curve_indices:
                    idx = curve_indices[0]
            if idx is None:
                curve_refs = op.get('curve_refs') or []
                if curve_refs:
                    idx = curve_refs[0].get('curve_index')
            return idx

        def get_curve(op):
            curves = editable_curves()
            idx = get_primary_curve_index(op)
            if idx is None:
                return None, "ERR_CURVE_INDEX_REQUIRED"
            if idx < 0 or idx >= len(curves):
                return None, "ERR_CURVE_NOT_FOUND"
            return curves[idx], None

        def get_selected_curves(op):
            curves = editable_curves()
            selected = []
            requested_indices = op.get('curve_indices')
            requested_refs = op.get('curve_refs') or []
            if requested_indices is None and requested_refs:
                requested_indices = [ref.get('curve_index') for ref in requested_refs]
            if not requested_indices:
                curve, curve_err = get_curve(op)
                if curve_err:
                    return None, curve_err
                return [curve], None
            for idx in requested_indices:
                if idx is None or idx < 0 or idx >= len(curves):
                    return None, "ERR_CURVE_NOT_FOUND"
                selected.append(curves[idx])
            return selected, None

        def editable_constraints():
            constraints = []
            for idx in range(s.geometricConstraints.count):
                constraints.append(s.geometricConstraints.item(idx))
            return constraints

        def get_constraint(op):
            constraints = editable_constraints()
            idx = op.get('constraint_index')
            if idx is None:
                constraint_ref = op.get('constraint_ref') or {}
                idx = constraint_ref.get('constraint_index')
            if idx is None:
                return None, "ERR_CONSTRAINT_INDEX_REQUIRED"
            if idx < 0 or idx >= len(constraints):
                return None, "ERR_CONSTRAINT_NOT_FOUND"
            return constraints[idx], None

        def editable_dimensions():
            dims = []
            for idx in range(s.sketchDimensions.count):
                dims.append(s.sketchDimensions.item(idx))
            return dims

        def get_dimension(op):
            dims = editable_dimensions()
            idx = op.get('dimension_index')
            if idx is None:
                dim_ref = op.get('dimension_ref') or {}
                idx = dim_ref.get('dimension_index')
            if idx is None:
                return None, "ERR_DIMENSION_INDEX_REQUIRED"
            if idx < 0 or idx >= len(dims):
                return None, "ERR_DIMENSION_NOT_FOUND"
            return dims[idx], None

        def get_curve_pair(op):
            pair_indices = op.get('curve_indices') or []
            pair_refs = op.get('curve_refs') or []
            curve_one_payload = {"curve_index": op.get("curve_index"), "curve_ref": op.get("curve_ref")}
            curve_two_payload = {"curve_index": op.get("other_curve_index"), "curve_ref": op.get("other_curve_ref")}
            if pair_indices:
                curve_one_payload["curve_index"] = pair_indices[0] if len(pair_indices) > 0 else None
                curve_two_payload["curve_index"] = pair_indices[1] if len(pair_indices) > 1 else None
            elif pair_refs:
                curve_one_payload["curve_ref"] = pair_refs[0] if len(pair_refs) > 0 else None
                curve_two_payload["curve_ref"] = pair_refs[1] if len(pair_refs) > 1 else None

            curve_one, err_one = get_curve(curve_one_payload)
            if err_one:
                return None, None, err_one
            curve_two, err_two = get_curve(curve_two_payload)
            if err_two:
                return None, None, err_two
            return curve_one, curve_two, None

        def get_mirror_axis(op):
            axis_idx = op.get('mirror_curve_index')
            if axis_idx is None:
                axis_ref = op.get('mirror_curve_ref') or {}
                axis_idx = axis_ref.get('curve_index')
            if axis_idx is None:
                return None, "ERR_MIRROR_AXIS_REQUIRED"
            axis_curve, axis_err = get_curve({"curve_index": axis_idx})
            if axis_err:
                return None, axis_err
            if 'SketchLine' not in getattr(axis_curve, 'objectType', ''):
                return None, "ERR_MIRROR_AXIS_INVALID"
            return axis_curve, None

        def get_text_point(op):
            return adsk.core.Point3D.create(float(op.get('text_x', 0)), float(op.get('text_y', 0)), 0)

        def get_dimension_orientation(name):
            orientation_name = str(name or "aligned").lower()
            if orientation_name == "horizontal":
                return adsk.fusion.DimensionOrientations.HorizontalDimensionOrientation
            if orientation_name == "vertical":
                return adsk.fusion.DimensionOrientations.VerticalDimensionOrientation
            return adsk.fusion.DimensionOrientations.AlignedDimensionOrientation

        def normalize_constraint_type(name):
            constraint_name = str(name or "").strip().lower()
            aliases = {
                "horizontalconstraint": "horizontal",
                "verticalconstraint": "vertical",
                "parallelconstraint": "parallel",
                "perpendicularconstraint": "perpendicular",
                "collinearconstraint": "collinear",
                "tangentconstraint": "tangent",
                "concentricconstraint": "concentric",
            }
            return aliases.get(constraint_name, constraint_name)

        def normalize_dimension_type(name):
            dimension_name = str(name or "").strip().lower()
            aliases = {
                "distancedimension": "distance",
                "radialdimension": "radial",
                "radiusdimension": "radial",
                "diameterdimension": "diameter",
                "angulardimension": "angular",
            }
            return aliases.get(dimension_name, dimension_name)

        def get_sketch_health_message():
            try:
                message = str(getattr(s, 'errorOrWarningMessage', '') or '').strip()
                return message
            except:
                return ""

        def get_component_plane_entity(component, plane_name):
            plane_key = str(plane_name or 'XY').upper()
            return {
                'XY': component.xYConstructionPlane,
                'XZ': component.xZConstructionPlane,
                'YZ': component.yZConstructionPlane,
            }.get(plane_key, component.xYConstructionPlane)

        def resolve_body_from_op(op, body_key='body'):
            body_name = op.get(body_key)
            if not body_name:
                return None, None, "ERR_BODY"
            return resolve_body_context(body_name, op.get('component_name'), op.get('component_path'))

        def get_faces_from_op(op):
            body, body_owner, body_err = resolve_body_from_op(op)
            if body_err:
                return None, None, body_err

            face_indices = op.get('face_indices')
            if face_indices is None:
                face_index = op.get('face_index')
                face_indices = [face_index] if face_index is not None else []
            if not face_indices:
                return None, None, "ERR_FACE_INDEX_REQUIRED"

            faces = []
            for idx in face_indices:
                idx = int(idx)
                if idx < 0 or idx >= body.faces.count:
                    return None, None, "ERR_FACE_INDEX"
                faces.append(body.faces.item(idx))
            return faces, body_owner, None

        def collect_projection_entities(op):
            entities = []
            selected_curves, curve_err = get_selected_curves(op)
            if not curve_err and selected_curves:
                entities.extend(selected_curves)

            body_name = op.get('body')
            if body_name:
                body, _, body_err = resolve_body_from_op(op)
                if body_err:
                    return None, body_err

                face_indices = op.get('face_indices')
                if face_indices is None and op.get('face_index') is not None:
                    face_indices = [op.get('face_index')]
                if face_indices:
                    for idx in face_indices:
                        idx = int(idx)
                        if idx < 0 or idx >= body.faces.count:
                            return None, "ERR_FACE_INDEX"
                        entities.append(body.faces.item(idx))
                else:
                    edge_indices = op.get('edge_indices')
                    if edge_indices is None and op.get('edge_index') is not None:
                        edge_indices = [op.get('edge_index')]
                    vertex_indices = op.get('vertex_indices')
                    if vertex_indices is None and op.get('vertex_index') is not None:
                        vertex_indices = [op.get('vertex_index')]

                    if edge_indices:
                        for idx in edge_indices:
                            idx = int(idx)
                            if idx < 0 or idx >= body.edges.count:
                                return None, "ERR_INVALID_ENTITY"
                            entities.append(body.edges.item(idx))
                    elif vertex_indices:
                        for idx in vertex_indices:
                            idx = int(idx)
                            if idx < 0 or idx >= body.vertices.count:
                                return None, "ERR_INVALID_ENTITY"
                            entities.append(body.vertices.item(idx))
                    else:
                        entities.append(body)

            if not entities:
                return None, "ERR_INVALID_ENTITY"
            return entities, None

        def resolve_projection_direction(op):
            direction_axis = op.get('direction_axis')
            if direction_axis:
                axis_name = str(direction_axis).lower()
                if axis_name == 'x':
                    return owner.xConstructionAxis, None
                if axis_name == 'y':
                    return owner.yConstructionAxis, None
                return owner.zConstructionAxis, None

            direction_curve_index = op.get('direction_curve_index')
            direction_curve_ref = op.get('direction_curve_ref')
            if direction_curve_index is not None or direction_curve_ref:
                return get_curve({"curve_index": direction_curve_index, "curve_ref": direction_curve_ref})

            return None, "ERR_DIRECTION_REQUIRED"

        def get_surface_project_type(name):
            project_type = str(name or 'closest_point').strip().lower()
            if project_type in ('closest_point', 'closest', 'closestpoint'):
                return adsk.fusion.SurfaceProjectTypes.ClosestPointSurfaceProjectType, None
            if project_type in ('along_vector', 'vector', 'alongvector'):
                return adsk.fusion.SurfaceProjectTypes.AlongVectorSurfaceProjectType, None
            return None, "ERR_UNKNOWN_PROJECTION_TYPE"

        def resolve_spun_profile_entities(op):
            body_names = op.get('bodies') or []
            if body_names:
                entities = []
                entity_owner = None
                for body_name in body_names:
                    target, target_owner, target_err = resolve_body_context(body_name, op.get('component_name'), op.get('component_path'))
                    if target_err or not target:
                        return None, None, target_err or "ERR_BODY"
                    if entity_owner is None:
                        entity_owner = target_owner
                    elif target_owner != entity_owner:
                        return None, None, "ERR_INVALID_ENTITY"
                    entities.append(target)
                return entities, entity_owner, None

            target, target_owner, target_err = resolve_body_context(op['body'], op.get('component_name'), op.get('component_path'))
            if target_err or not target:
                return None, None, target_err or "ERR_BODY"

            face_indices = op.get('face_indices')
            if face_indices is None and op.get('face_index') is not None:
                face_indices = [op.get('face_index')]

            if face_indices:
                entities = []
                for face_index in face_indices:
                    face_index = int(face_index)
                    if face_index < 0 or face_index >= target.faces.count:
                        return None, None, "ERR_FACE_INDEX"
                    entities.append(target.faces.item(face_index))
                return entities, target_owner, None

            return [target], target_owner, None

        def resolve_spun_profile_axis(op, default_owner):
            axis_curve_index = op.get('axis_curve_index')
            axis_curve_ref = op.get('axis_curve_ref')
            if axis_curve_index is not None or axis_curve_ref:
                return get_curve({"curve_index": axis_curve_index, "curve_ref": axis_curve_ref})

            axis_body_name = op.get('axis_body')
            axis_edge_index = op.get('axis_edge_index')
            if axis_edge_index is not None:
                axis_body_name = axis_body_name or op.get('body')
                if not axis_body_name:
                    return None, "ERR_INVALID_ENTITY"
                axis_body, _, axis_body_err = resolve_body_context(axis_body_name, op.get('component_name'), op.get('component_path'))
                if axis_body_err or not axis_body:
                    return None, axis_body_err or "ERR_BODY"
                edge_index = int(axis_edge_index)
                if edge_index < 0 or edge_index >= axis_body.edges.count:
                    return None, "ERR_INVALID_ENTITY"
                axis_edge = axis_body.edges.item(edge_index)
                if not hasattr(axis_edge, 'geometry') or 'Line3D' not in getattr(axis_edge.geometry, 'objectType', ''):
                    return None, "ERR_INVALID_ENTITY"
                return axis_edge, None

            axis_name = str(op.get('axis', 'z')).lower()
            if axis_name == 'x':
                return default_owner.xConstructionAxis, None
            if axis_name == 'y':
                return default_owner.yConstructionAxis, None
            return default_owner.zConstructionAxis, None

        def project_entities_to_sketch(entities, is_linked=False):
            if hasattr(s, 'project2'):
                return s.project2(entities, bool(is_linked))

            if len(entities) == 1:
                return s.project(entities[0])

            collection = adsk.core.ObjectCollection.create()
            for entity in entities:
                collection.add(entity)
            return s.project(collection)

        def add_center_to_center_slot(start_point, end_point, width_value):
            if hasattr(s, 'addCenterToCenterSlot'):
                s.addCenterToCenterSlot(start_point, end_point, width_value)
                return

            width_real = width_value.value if hasattr(width_value, 'value') else float(width_value)
            dx = end_point.x - start_point.x
            dy = end_point.y - start_point.y
            length = math.hypot(dx, dy)
            if length <= 1e-9:
                raise ValueError('slot length must be greater than zero')

            radius = width_real / 2.0
            ux = dx / length
            uy = dy / length
            px = -uy
            py = ux

            start_top = adsk.core.Point3D.create(start_point.x + (px * radius), start_point.y + (py * radius), 0)
            start_bottom = adsk.core.Point3D.create(start_point.x - (px * radius), start_point.y - (py * radius), 0)
            end_top = adsk.core.Point3D.create(end_point.x + (px * radius), end_point.y + (py * radius), 0)
            end_bottom = adsk.core.Point3D.create(end_point.x - (px * radius), end_point.y - (py * radius), 0)

            s.sketchCurves.sketchArcs.addByCenterStartSweep(start_point, start_top, math.pi)
            s.sketchCurves.sketchArcs.addByCenterStartSweep(end_point, end_bottom, math.pi)
            s.sketchCurves.sketchLines.addByTwoPoints(start_top, end_top)
            s.sketchCurves.sketchLines.addByTwoPoints(start_bottom, end_bottom)

        def add_overall_slot(start_point, end_point, width_value):
            if hasattr(s, 'addOverallSlot'):
                s.addOverallSlot(start_point, end_point, width_value)
                return

            width_real = width_value.value if hasattr(width_value, 'value') else float(width_value)
            dx = end_point.x - start_point.x
            dy = end_point.y - start_point.y
            length = math.hypot(dx, dy)
            if length <= width_real:
                raise ValueError('overall slot length must be greater than width')

            inset = width_real / 2.0
            ux = dx / length
            uy = dy / length
            center_start = adsk.core.Point3D.create(start_point.x + (ux * inset), start_point.y + (uy * inset), 0)
            center_end = adsk.core.Point3D.create(end_point.x - (ux * inset), end_point.y - (uy * inset), 0)
            add_center_to_center_slot(center_start, center_end, width_value)

        def add_center_point_slot(center_point, direction_point, width_value):
            if hasattr(s, 'addCenterPointSlot'):
                s.addCenterPointSlot(center_point, direction_point, width_value)
                return

            width_real = width_value.value if hasattr(width_value, 'value') else float(width_value)
            dx = direction_point.x - center_point.x
            dy = direction_point.y - center_point.y
            if math.hypot(dx, dy) <= 1e-9:
                raise ValueError('slot direction point must differ from center point')

            start_point = adsk.core.Point3D.create(center_point.x - dx, center_point.y - dy, 0)
            end_point = adsk.core.Point3D.create(direction_point.x, direction_point.y, 0)
            add_center_to_center_slot(start_point, end_point, adsk.core.ValueInput.createByReal(width_real))

        def add_regular_polygon(center_x, center_y, radius, sides, rotation_radians=0.0):
            if sides < 3:
                raise ValueError('polygon requires at least 3 sides')

            pts = []
            for i in range(sides):
                angle = rotation_radians + (i * 2.0 * math.pi / sides)
                pts.append(adsk.core.Point3D.create(center_x + radius * math.cos(angle), center_y + radius * math.sin(angle), 0))
            for i in range(sides):
                s.sketchCurves.sketchLines.addByTwoPoints(pts[i], pts[(i + 1) % sides])

        def add_center_rectangle(center_point, corner_point):
            if hasattr(s.sketchCurves.sketchLines, 'addCenterPointRectangle'):
                s.sketchCurves.sketchLines.addCenterPointRectangle(center_point, corner_point)
                return

            dx = corner_point.x - center_point.x
            dy = corner_point.y - center_point.y
            p1 = adsk.core.Point3D.create(center_point.x - dx, center_point.y - dy, 0)
            p2 = adsk.core.Point3D.create(center_point.x + dx, center_point.y + dy, 0)
            s.sketchCurves.sketchLines.addTwoPointRectangle(p1, p2)

        def add_three_point_rectangle(point_one, point_two, point_three):
            if hasattr(s.sketchCurves.sketchLines, 'addThreePointRectangle'):
                s.sketchCurves.sketchLines.addThreePointRectangle(point_one, point_two, point_three)
                return

            vx = point_two.x - point_one.x
            vy = point_two.y - point_one.y
            length = math.hypot(vx, vy)
            if length <= 1e-9:
                raise ValueError('rectangle base length must be greater than zero')

            nx = -vy / length
            ny = vx / length
            offset = ((point_three.x - point_one.x) * nx) + ((point_three.y - point_one.y) * ny)
            point_four = adsk.core.Point3D.create(point_two.x + (nx * offset), point_two.y + (ny * offset), 0)
            point_three_projected = adsk.core.Point3D.create(point_one.x + (nx * offset), point_one.y + (ny * offset), 0)
            s.sketchCurves.sketchLines.addByTwoPoints(point_one, point_two)
            s.sketchCurves.sketchLines.addByTwoPoints(point_two, point_four)
            s.sketchCurves.sketchLines.addByTwoPoints(point_four, point_three_projected)
            s.sketchCurves.sketchLines.addByTwoPoints(point_three_projected, point_one)

        def add_edge_polygon(point_one, point_two, sides, flip=False):
            if sides < 3:
                raise ValueError('polygon requires at least 3 sides')

            dx = point_two.x - point_one.x
            dy = point_two.y - point_one.y
            edge_length = math.hypot(dx, dy)
            if edge_length <= 1e-9:
                raise ValueError('polygon edge length must be greater than zero')

            interior_angle = math.pi / sides
            radius = edge_length / (2.0 * math.sin(interior_angle))
            midpoint = adsk.core.Point3D.create((point_one.x + point_two.x) / 2.0, (point_one.y + point_two.y) / 2.0, 0)
            nx = -dy / edge_length
            ny = dx / edge_length
            if flip:
                nx = -nx
                ny = -ny
            apothem = radius * math.cos(interior_angle)
            center_x = midpoint.x + (nx * apothem)
            center_y = midpoint.y + (ny * apothem)
            start_angle = math.atan2(point_one.y - center_y, point_one.x - center_x)
            add_regular_polygon(center_x, center_y, radius, sides, start_angle)

        results = []
        for op in params.get('operations', []):
            action = op.get('action')
            try:
                if action == 'draw_line':
                    p1 = adsk.core.Point3D.create(op['x1'], op['y1'], 0)
                    p2 = adsk.core.Point3D.create(op['x2'], op['y2'], 0)
                    s.sketchCurves.sketchLines.addByTwoPoints(p1, p2)
                    results.append(f"{action}:OK")
                elif action == 'draw_circle':
                    center = adsk.core.Point3D.create(op['x'], op['y'], 0)
                    r = float(op.get('radius', op.get('r', 0)))
                    s.sketchCurves.sketchCircles.addByCenterRadius(center, r)
                    results.append(f"{action}:OK")
                elif action == 'draw_rectangle':
                    p1 = adsk.core.Point3D.create(op['x1'], op['y1'], 0)
                    p2 = adsk.core.Point3D.create(op['x2'], op['y2'], 0)
                    s.sketchCurves.sketchLines.addTwoPointRectangle(p1, p2)
                    results.append(f"{action}:OK")
                elif action == 'draw_center_rectangle':
                    center = adsk.core.Point3D.create(op['cx'], op['cy'], 0)
                    corner = adsk.core.Point3D.create(op['x'], op['y'], 0)
                    add_center_rectangle(center, corner)
                    results.append(f"{action}:OK")
                elif action == 'draw_three_point_rectangle':
                    p1 = adsk.core.Point3D.create(op['x1'], op['y1'], 0)
                    p2 = adsk.core.Point3D.create(op['x2'], op['y2'], 0)
                    p3 = adsk.core.Point3D.create(op['x3'], op['y3'], 0)
                    add_three_point_rectangle(p1, p2, p3)
                    results.append(f"{action}:OK")
                elif action == 'draw_polygon':
                    cx, cy = float(op['cx']), float(op['cy'])
                    r = float(op.get('radius', op.get('r', 0)))
                    n = int(op.get('sides', 6))
                    add_regular_polygon(cx, cy, r, n)
                    results.append(f"{action}:OK")
                elif action == 'draw_inscribed_polygon':
                    cx, cy = float(op['cx']), float(op['cy'])
                    r = float(op.get('radius', op.get('r', 0)))
                    n = int(op.get('sides', 6))
                    add_regular_polygon(cx, cy, r, n)
                    results.append(f"{action}:OK")
                elif action == 'draw_circumscribed_polygon':
                    cx, cy = float(op['cx']), float(op['cy'])
                    apothem = float(op.get('radius', op.get('r', 0)))
                    n = int(op.get('sides', 6))
                    radius = apothem / math.cos(math.pi / n)
                    add_regular_polygon(cx, cy, radius, n)
                    results.append(f"{action}:OK")
                elif action == 'draw_edge_polygon':
                    p1 = adsk.core.Point3D.create(op['x1'], op['y1'], 0)
                    p2 = adsk.core.Point3D.create(op['x2'], op['y2'], 0)
                    n = int(op.get('sides', 6))
                    add_edge_polygon(p1, p2, n, bool(op.get('flip', False)))
                    results.append(f"{action}:OK")
                elif action == 'draw_arc':
                    center = adsk.core.Point3D.create(op['cx'], op['cy'], 0)
                    start = adsk.core.Point3D.create(op['sx'], op['sy'], 0)
                    angle = (float(op['angle']) * math.pi) / 180.0
                    s.sketchCurves.sketchArcs.addByCenterStartSweep(center, start, angle)
                    results.append(f"{action}:OK")
                elif action == 'draw_spline':
                    points = adsk.core.ObjectCollection.create()
                    for p in op['pts']:
                        points.add(adsk.core.Point3D.create(p[0], p[1], 0))
                    s.sketchCurves.sketchFittedSplines.add(points)
                    results.append(f"{action}:OK")
                elif action == 'draw_slot':
                    p1 = adsk.core.Point3D.create(op['x1'], op['y1'], 0)
                    p2 = adsk.core.Point3D.create(op['x2'], op['y2'], 0)
                    width = adsk.core.ValueInput.createByReal(float(op.get('width', op.get('w', 0))))
                    add_center_to_center_slot(p1, p2, width)
                    results.append(f"{action}:OK")
                elif action == 'draw_overall_slot':
                    p1 = adsk.core.Point3D.create(op['x1'], op['y1'], 0)
                    p2 = adsk.core.Point3D.create(op['x2'], op['y2'], 0)
                    width = adsk.core.ValueInput.createByReal(float(op.get('width', op.get('w', 0))))
                    add_overall_slot(p1, p2, width)
                    results.append(f"{action}:OK")
                elif action == 'draw_center_point_slot':
                    center = adsk.core.Point3D.create(op['cx'], op['cy'], 0)
                    direction = adsk.core.Point3D.create(op['x'], op['y'], 0)
                    width = adsk.core.ValueInput.createByReal(float(op.get('width', op.get('w', 0))))
                    add_center_point_slot(center, direction, width)
                    results.append(f"{action}:OK")
                elif action == 'draw_ellipse':
                    center = adsk.core.Point3D.create(op['cx'], op['cy'], 0)
                    major = adsk.core.Point3D.create(op['mx'], op['my'], 0)
                    on_ellipse = adsk.core.Point3D.create(op['ox'], op['oy'], 0)
                    s.sketchCurves.sketchEllipses.add(center, major, on_ellipse)
                    results.append(f"{action}:OK")
                elif action == 'draw_text':
                    texts = s.sketchTexts
                    point = adsk.core.Point3D.create(float(op['x']), float(op['y']), 0)
                    height = float(op.get('height', 1.0))
                    text_input = texts.createInput(str(op['text']), height, point)
                    if op.get('font'):
                        text_input.fontName = str(op['font'])
                    texts.add(text_input)
                    results.append(f"{action}:OK")
                elif action == 'import_svg':
                    imported = s.importSVG(
                        str(op['path']),
                        float(op.get('x', 0)),
                        float(op.get('y', 0)),
                        float(op.get('scale', 1.0))
                    )
                    if imported:
                        results.append(f"{action}:OK")
                    else:
                        health_message = get_sketch_health_message()
                        results.append(f"{action}:ERR:{health_message if health_message else 'SVG import failed'}")
                elif action == 'create_spun_profile':
                    entities, entities_owner, target_err = resolve_spun_profile_entities(op)
                    if not entities:
                        results.append(f"{action}:{target_err or 'ERR_BODY'}")
                    else:
                        spun_input = s.createSpunProfileInput()
                        spun_input.entities = entities

                        axis_entity, axis_err = resolve_spun_profile_axis(op, entities_owner or owner)
                        if axis_err:
                            results.append(f"{action}:{axis_err}")
                            continue
                        spun_input.axis = axis_entity
                        if op.get('flip_result') is not None:
                            spun_input.flipResult = bool(op.get('flip_result'))
                        if op.get('is_axis_projected') is not None:
                            spun_input.isAxisProjected = bool(op.get('is_axis_projected'))
                        if op.get('is_centerline_added') is not None:
                            spun_input.isCenterlineAdded = bool(op.get('is_centerline_added'))
                        if op.get('tolerance') is not None:
                            spun_input.tolerance = float(op.get('tolerance'))

                        spun_result = s.createSpunProfile(spun_input)
                        if spun_result:
                            results.append(f"{action}:OK")
                        else:
                            health_message = get_sketch_health_message()
                            results.append(f"{action}:ERR:{health_message if health_message else 'Spun profile creation failed'}")
                elif action == 'project_geometry':
                    entities, entity_err = collect_projection_entities(op)
                    if entity_err:
                        results.append(f"{action}:{entity_err}")
                    else:
                        project_entities_to_sketch(entities, bool(op.get('is_linked', False)))
                        results.append(f"{action}:OK")
                elif action == 'project_cut_edges':
                    body, _, body_err = resolve_body_from_op(op)
                    if body_err:
                        results.append(f"{action}:{body_err}")
                    else:
                        s.projectCutEdges(body)
                        results.append(f"{action}:OK")
                elif action == 'include_geometry':
                    entities, entity_err = collect_projection_entities(op)
                    if entity_err:
                        results.append(f"{action}:{entity_err}")
                    else:
                        for entity in entities:
                            s.include(entity)
                        results.append(f"{action}:OK")
                elif action == 'project_to_surface':
                    faces, _, face_err = get_faces_from_op(op)
                    if face_err:
                        results.append(f"{action}:{face_err}")
                    else:
                        source_curves, curve_err = get_selected_curves(op)
                        if curve_err:
                            results.append(f"{action}:{curve_err}")
                        else:
                            project_type, type_err = get_surface_project_type(op.get('projection_type'))
                            if type_err:
                                results.append(f"{action}:{type_err}")
                            else:
                                if project_type == adsk.fusion.SurfaceProjectTypes.AlongVectorSurfaceProjectType:
                                    direction_entity, direction_err = resolve_projection_direction(op)
                                    if direction_err:
                                        results.append(f"{action}:{direction_err}")
                                        continue
                                    s.projectToSurface(faces, source_curves, project_type, direction_entity)
                                else:
                                    s.projectToSurface(faces, source_curves, project_type)
                                results.append(f"{action}:OK")
                elif action == 'redefine':
                    target_plane = None
                    if op.get('body') is not None:
                        faces, _, face_err = get_faces_from_op(op)
                        if face_err:
                            results.append(f"{action}:{face_err}")
                            continue
                        target_plane = faces[0]
                    else:
                        target_plane = get_component_plane_entity(owner, op.get('plane_name', op.get('plane')))

                    redefine_ok = False
                    if hasattr(s, 'referencePlane'):
                        s.referencePlane = target_plane
                        redefine_ok = True
                    elif hasattr(s, 'redefine'):
                        redefine_ok = bool(s.redefine(target_plane))

                    if redefine_ok:
                        results.append(f"{action}:OK")
                    else:
                        health_message = get_sketch_health_message()
                        results.append(f"{action}:ERR:{health_message if health_message else 'Sketch redefine failed'}")
                elif action == 'find_connected_curves':
                    seed_curve, curve_err = get_curve(op)
                    if curve_err:
                        results.append(f"{action}:{curve_err}")
                    else:
                        connected = s.findConnectedCurves(seed_curve)
                        results.append(f"{action}:OK:{connected.count if hasattr(connected, 'count') else len(connected)}")
                elif action == 'offset':
                    entities = adsk.core.ObjectCollection.create()
                    seed_curve_index = op.get('seed_curve_index')
                    seed_curve_ref = op.get('seed_curve_ref')
                    if seed_curve_index is not None or seed_curve_ref:
                        seed_curve, curve_err = get_curve({"curve_index": seed_curve_index, "curve_ref": seed_curve_ref})
                        if curve_err:
                            results.append(f"{action}:{curve_err}")
                            continue
                        connected = s.findConnectedCurves(seed_curve)
                        if hasattr(connected, 'count'):
                            for idx in range(connected.count):
                                entities.add(connected.item(idx))
                        else:
                            for curve in connected:
                                entities.add(curve)
                    else:
                        selected = op.get('curve_indices')
                        curves = editable_curves()
                        if selected:
                            for idx in selected:
                                if idx < 0 or idx >= len(curves):
                                    raise ValueError(f"curve index {idx} out of range")
                                entities.add(curves[idx])
                        else:
                            for curve in curves:
                                entities.add(curve)
                    if entities.count < 1:
                        results.append(f"{action}:ERR_EMPTY")
                    else:
                        offset_x = float(op.get('x', 10.0))
                        offset_y = float(op.get('y', 10.0))
                        s.offset(entities, adsk.core.Point3D.create(offset_x, offset_y, 0), float(op['dist']))
                        results.append(f"{action}:OK")
                elif action == 'circular_pattern':
                    curves = editable_curves()
                    if len(curves) < 1:
                        results.append(f"{action}:ERR_EMPTY")
                    else:
                        center_point = s.sketchPoints.add(adsk.core.Point3D.create(op['cx'], op['cy'], 0))
                        pattern_input = s.geometricConstraints.createCircularPatternInput(curves, center_point)
                        pattern_input.quantity = adsk.core.ValueInput.createByReal(op['count'])
                        pattern_input.totalAngle = adsk.core.ValueInput.createByString(op.get('total_angle', '360 deg'))
                        s.geometricConstraints.addCircularPattern(pattern_input)
                        results.append(f"{action}:OK")
                elif action == 'rectangular_pattern':
                    curves = editable_curves()
                    if len(curves) < 1:
                        results.append(f"{action}:ERR_EMPTY")
                    else:
                        pattern_input = s.geometricConstraints.createRectangularPatternInput(
                            curves,
                            adsk.fusion.PatternDistanceType.SpacingPatternDistanceType,
                        )
                        lines = s.sketchCurves.sketchLines
                        dir1 = next((l for l in lines if l.isConstruction), None)
                        if not dir1:
                            dir1 = lines.addByTwoPoints(adsk.core.Point3D.create(0,0,0), adsk.core.Point3D.create(1,0,0))
                            dir1.isConstruction = True
                        pattern_input.setDirectionOne(
                            dir1,
                            adsk.core.ValueInput.createByReal(op['count_x']),
                            adsk.core.ValueInput.createByReal(op['dist_x']),
                        )
                        count_y = int(op.get('count_y', 1))
                        if count_y > 1:
                            dir2 = next((l for l in lines if l.isConstruction and l != dir1), None)
                            if not dir2:
                                dir2 = lines.addByTwoPoints(adsk.core.Point3D.create(0,0,0), adsk.core.Point3D.create(0,1,0))
                                dir2.isConstruction = True
                            pattern_input.setDirectionTwo(
                                dir2,
                                adsk.core.ValueInput.createByReal(count_y),
                                adsk.core.ValueInput.createByReal(op.get('dist_y', 0)),
                            )
                        s.geometricConstraints.addRectangularPattern(pattern_input)
                        results.append(f"{action}:OK")
                elif action == 'delete_curve':
                    curve, curve_err = get_curve(op)
                    if curve_err:
                        results.append(f"{action}:{curve_err}")
                    else:
                        curve.deleteMe()
                        results.append(f"{action}:OK")
                elif action == 'move_entities':
                    selected_curves, curve_err = get_selected_curves(op)
                    if curve_err:
                        results.append(f"{action}:{curve_err}")
                    else:
                        entities = adsk.core.ObjectCollection.create()
                        for curve in selected_curves:
                            entities.add(curve)
                        transform = adsk.core.Matrix3D.create()
                        transform.translation = adsk.core.Vector3D.create(
                            float(op.get('dx', op.get('x', 0))),
                            float(op.get('dy', op.get('y', 0))),
                            0
                        )
                        s.move(entities, transform)
                        results.append(f"{action}:OK")
                elif action == 'copy_entities':
                    selected_curves, curve_err = get_selected_curves(op)
                    if curve_err:
                        results.append(f"{action}:{curve_err}")
                    else:
                        entities = adsk.core.ObjectCollection.create()
                        for curve in selected_curves:
                            entities.add(curve)
                        transform = adsk.core.Matrix3D.create()
                        transform.translation = adsk.core.Vector3D.create(
                            float(op.get('dx', op.get('x', 0))),
                            float(op.get('dy', op.get('y', 0))),
                            0
                        )
                        s.copy(entities, transform)
                        results.append(f"{action}:OK")
                elif action == 'mirror_entities':
                    selected_curves, curve_err = get_selected_curves(op)
                    if curve_err:
                        results.append(f"{action}:{curve_err}")
                    else:
                        axis_curve, axis_err = get_mirror_axis(op)
                        if axis_err:
                            results.append(f"{action}:{axis_err}")
                        else:
                            start_pt = axis_curve.startSketchPoint.geometry
                            end_pt = axis_curve.endSketchPoint.geometry
                            axis_dx = end_pt.x - start_pt.x
                            axis_dy = end_pt.y - start_pt.y
                            axis_length = math.hypot(axis_dx, axis_dy)
                            if axis_length <= 1e-9:
                                results.append(f"{action}:ERR_MIRROR_AXIS_INVALID")
                            else:
                                ux = axis_dx / axis_length
                                uy = axis_dy / axis_length
                                r00 = (2.0 * ux * ux) - 1.0
                                r01 = 2.0 * ux * uy
                                r10 = 2.0 * ux * uy
                                r11 = (2.0 * uy * uy) - 1.0
                                tx = start_pt.x - ((r00 * start_pt.x) + (r01 * start_pt.y))
                                ty = start_pt.y - ((r10 * start_pt.x) + (r11 * start_pt.y))

                                entities = adsk.core.ObjectCollection.create()
                                for curve in selected_curves:
                                    entities.add(curve)

                                transform = adsk.core.Matrix3D.create()
                                transform.setCell(0, 0, r00)
                                transform.setCell(0, 1, r01)
                                transform.setCell(1, 0, r10)
                                transform.setCell(1, 1, r11)
                                transform.setCell(0, 3, tx)
                                transform.setCell(1, 3, ty)
                                s.copy(entities, transform)
                                results.append(f"{action}:OK")
                elif action == 'set_construction':
                    curve, curve_err = get_curve(op)
                    if curve_err:
                        results.append(f"{action}:{curve_err}")
                    else:
                        curve.isConstruction = bool(op.get('value', True))
                        results.append(f"{action}:OK")
                elif action == 'trim':
                    curve, curve_err = get_curve(op)
                    if curve_err:
                        results.append(f"{action}:{curve_err}")
                    else:
                        trim_point = adsk.core.Point3D.create(op['x'], op['y'], 0)
                        curve.trim(trim_point)
                        results.append(f"{action}:OK")
                elif action == 'clear_sketch':
                    try:
                        s.isComputeDeferred = True
                    except:
                        pass
                    while s.sketchDimensions.count > 0:
                        try:
                            s.sketchDimensions.item(s.sketchDimensions.count - 1).deleteMe()
                        except:
                            break
                    while s.geometricConstraints.count > 0:
                        try:
                            constraint = s.geometricConstraints.item(s.geometricConstraints.count - 1)
                            if hasattr(constraint, 'isDeletable') and not constraint.isDeletable:
                                break
                            constraint.deleteMe()
                        except:
                            break
                    while s.sketchTexts.count > 0:
                        try:
                            s.sketchTexts.item(s.sketchTexts.count - 1).deleteMe()
                        except:
                            break
                    while True:
                        try:
                            curves = editable_curves()
                        except:
                            curves = []
                        if not curves:
                            break
                        deleted_any = False
                        for curve in reversed(curves):
                            try:
                                curve.deleteMe()
                                deleted_any = True
                            except:
                                continue
                        if not deleted_any:
                            break
                    try:
                        s.isComputeDeferred = False
                    except:
                        pass
                    results.append(f"{action}:OK")
                elif action == 'add_constraint':
                    constraints = s.geometricConstraints
                    constraint_type = normalize_constraint_type(op.get('type', ''))
                    if constraint_type in ('horizontal', 'vertical'):
                        curve, curve_err = get_curve(op)
                        if curve_err:
                            results.append(f"{action}:{curve_err}")
                        elif 'SketchLine' not in getattr(curve, 'objectType', ''):
                            results.append(f"{action}:ERR_INVALID_ENTITY")
                        else:
                            if constraint_type == 'horizontal':
                                constraints.addHorizontal(curve)
                            else:
                                constraints.addVertical(curve)
                            results.append(f"{action}:OK")
                    elif constraint_type in ('parallel', 'perpendicular', 'collinear'):
                        curve_one, curve_two, curve_err = get_curve_pair(op)
                        if curve_err:
                            results.append(f"{action}:{curve_err}")
                        elif 'SketchLine' not in getattr(curve_one, 'objectType', '') or 'SketchLine' not in getattr(curve_two, 'objectType', ''):
                            results.append(f"{action}:ERR_INVALID_ENTITY")
                        else:
                            if constraint_type == 'parallel':
                                constraints.addParallel(curve_one, curve_two)
                            elif constraint_type == 'perpendicular':
                                constraints.addPerpendicular(curve_one, curve_two)
                            else:
                                constraints.addCollinear(curve_one, curve_two)
                            results.append(f"{action}:OK")
                    elif constraint_type == 'tangent':
                        curve_one, curve_two, curve_err = get_curve_pair(op)
                        if curve_err:
                            results.append(f"{action}:{curve_err}")
                        else:
                            constraints.addTangent(curve_one, curve_two)
                            results.append(f"{action}:OK")
                    elif constraint_type == 'concentric':
                        curve_one, curve_two, curve_err = get_curve_pair(op)
                        if curve_err:
                            results.append(f"{action}:{curve_err}")
                        else:
                            constraints.addConcentric(curve_one, curve_two)
                            results.append(f"{action}:OK")
                    else:
                        results.append(f"{action}:ERR_UNKNOWN_CONSTRAINT_TYPE")
                elif action == 'remove_constraint':
                    constraint, constraint_err = get_constraint(op)
                    if constraint_err:
                        results.append(f"{action}:{constraint_err}")
                    else:
                        if hasattr(constraint, 'isDeletable') and not constraint.isDeletable:
                            results.append(f"{action}:ERR_CONSTRAINT_NOT_DELETABLE")
                        else:
                            constraint.deleteMe()
                            results.append(f"{action}:OK")
                elif action == 'set_dimension':
                    dimension, dimension_err = get_dimension(op)
                    if dimension_err:
                        results.append(f"{action}:{dimension_err}")
                    else:
                        dimension.value = float(op['value'])
                        results.append(f"{action}:OK")
                elif action == 'delete_dimension':
                    dimension, dimension_err = get_dimension(op)
                    if dimension_err:
                        results.append(f"{action}:{dimension_err}")
                    else:
                        if hasattr(dimension, 'isDeletable') and not dimension.isDeletable:
                            results.append(f"{action}:ERR_DIMENSION_NOT_DELETABLE")
                        else:
                            dimension.deleteMe()
                            results.append(f"{action}:OK")
                elif action == 'add_dimension':
                    dims = s.sketchDimensions
                    dimension_type = normalize_dimension_type(op.get('type', ''))
                    if dimension_type == 'distance':
                        curve, single_curve_err = get_curve(op)
                        if not single_curve_err and hasattr(curve, 'startSketchPoint') and hasattr(curve, 'endSketchPoint') and op.get('other_curve_index') is None and not op.get('other_curve_ref') and not op.get('curve_indices') and not op.get('curve_refs'):
                            dims.addDistanceDimension(
                                curve.startSketchPoint,
                                curve.endSketchPoint,
                                get_dimension_orientation(op.get('orientation')),
                                get_text_point(op),
                                bool(op.get('is_driving', True)),
                            )
                            results.append(f"{action}:OK")
                        else:
                            curve_one, curve_two, curve_err = get_curve_pair(op)
                            if curve_err:
                                results.append(f"{action}:{curve_err}")
                            elif not hasattr(curve_one, 'startSketchPoint') or not hasattr(curve_two, 'startSketchPoint'):
                                results.append(f"{action}:ERR_INVALID_ENTITY")
                            else:
                                dims.addDistanceDimension(
                                    curve_one.startSketchPoint,
                                    curve_two.startSketchPoint,
                                    get_dimension_orientation(op.get('orientation')),
                                    get_text_point(op),
                                    bool(op.get('is_driving', True)),
                                )
                                results.append(f"{action}:OK")
                    elif dimension_type == 'radial':
                        curve, curve_err = get_curve(op)
                        if curve_err:
                            results.append(f"{action}:{curve_err}")
                        else:
                            dims.addRadialDimension(curve, get_text_point(op), bool(op.get('is_driving', True)))
                            results.append(f"{action}:OK")
                    elif dimension_type == 'diameter':
                        curve, curve_err = get_curve(op)
                        if curve_err:
                            results.append(f"{action}:{curve_err}")
                        else:
                            dims.addDiameterDimension(curve, get_text_point(op), bool(op.get('is_driving', True)))
                            results.append(f"{action}:OK")
                    elif dimension_type == 'angular':
                        curve_one, curve_two, curve_err = get_curve_pair(op)
                        if curve_err:
                            results.append(f"{action}:{curve_err}")
                        elif 'SketchLine' not in getattr(curve_one, 'objectType', '') or 'SketchLine' not in getattr(curve_two, 'objectType', ''):
                            results.append(f"{action}:ERR_INVALID_ENTITY")
                        else:
                            dims.addAngularDimension(curve_one, curve_two, get_text_point(op), bool(op.get('is_driving', True)))
                            results.append(f"{action}:OK")
                    else:
                        results.append(f"{action}:ERR_UNKNOWN_DIMENSION_TYPE")
                else:
                    results.append(f"{action}:ERR_UNKNOWN_ACTION")
            except Exception as e:
                health_message = get_sketch_health_message()
                results.append(f"{action}:ERR:{health_message if health_message else str(e)}")
        returnValue.append(",".join(results) if results else "OK")
    else:
        returnValue.append("ERR_SKETCH_NOT_FOUND")
except Exception as e:
    returnValue.append(f"ERR_API:{str(e)}")
"""
