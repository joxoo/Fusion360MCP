def build_apply_custom_thread_script() -> str:
    return """try:
    body = find_body_recursive(root, params['body_name'])
    if not body:
        returnValue.append("ERR_BODY")
    else:
        threads = body.parentComponent.features.threadFeatures
        face = next((f for f in body.faces if f.geometry.surfaceType == adsk.core.SurfaceTypes.CylinderSurfaceType), None)
        if not face:
            returnValue.append("ERR_FACE")
        else:
            q = threads.threadDataQuery
            t_type = params['type']
            if t_type not in q.allThreadTypes:
                returnValue.append("ERR_TYPE")
            else:
                all_sizes = q.allSizes(t_type)
                target_size = str(params['size'])
                if target_size not in all_sizes:
                    try: target_size = "{:.1f}".format(float(params['size']))
                    except: pass
                if target_size not in all_sizes:
                    returnValue.append("ERR_SIZE")
                else:
                    target_desig = params['designation']
                    all_desigs = q.allDesignations(t_type, target_size)
                    if target_desig not in all_desigs:
                        returnValue.append("ERR_DESIG")
                    else:
                        classes = q.allClasses(False, t_type, target_desig)
                        target_class = params['class']
                        actual_class = target_class if target_class in classes else (classes[0] if len(classes) > 0 else "")
                        (res, sp) = face.evaluator.getPointAtParameter(adsk.core.Point2D.create(0.5, 0.5))
                        (res, normal) = face.evaluator.getNormalAtPoint(sp)
                        axis_pt = face.geometry.origin
                        vec_to_axis = axis_pt.asVector()
                        vec_to_axis.subtract(sp.asVector())
                        is_internal = normal.dotProduct(vec_to_axis) > 0
                        t_info = adsk.fusion.ThreadInfo.create(False, is_internal, t_type, target_desig, actual_class, True)
                        t_input = threads.createInput(face, t_info)
                        t_input.isModeled = params['modeled']
                        threads.add(t_input)
                        returnValue.append(target_desig)
except Exception as e:
    returnValue.append(f"ERR_API:{str(e)}")"""
