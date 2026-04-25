from core.bridge import execute_fusion_script, FusionBridgeError
from core.utils import format_response, register_tool

def apply_custom_thread_logic(body_name: str, thread_type: str, size: str, designation: str, thread_class: str = "", is_modeled: bool = True, lang: str = "en"):
    """Business logic for applying specific thread data."""
    script = """
try:
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
    returnValue.append(f"ERR_API:{str(e)}")
"""
    try:
        res = execute_fusion_script(script, {
            "body_name": body_name, "type": thread_type, "size": size,
            "designation": designation, "class": thread_class, "modeled": is_modeled
        }, use_common=["find_body"])
        val = res.get("data", ["ERR_UNKNOWN"])[0]
        if val == "ERR_BODY": return format_response(lang, "body_not_found")
        if val == "ERR_FACE": return format_response(lang, "face_not_found")
        if val == "ERR_TYPE": return format_response(lang, "thread_type_not_found")
        if val == "ERR_SIZE": return format_response(lang, "size_not_found")
        if val == "ERR_DESIG": return format_response(lang, "designation_not_found")
        if val.startswith("ERR_"): return format_response(lang, "unknown_error")
        return format_response(lang, "thread_applied", name=val)
    except FusionBridgeError as e: return f"Error: {str(e)}"

def register_thread_tools(mcp):
    register_tool(mcp, "apply_custom_thread", apply_custom_thread_logic)
