from core.bridge import execute_fusion_script, get_i18n_data, FusionBridgeError
from core.utils import get_tool_definition, format_response
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
I18N = get_i18n_data(os.path.join(BASE_DIR, "i18n.json"))

def apply_custom_thread_logic(body_name: str, thread_type: str, size: str, designation: str, thread_class: str, is_modeled: bool, lang: str):
    """Business logic for applying specific thread data using ThreadInfo.create."""
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
            
            # Validation (Finding 1 & 2)
            if t_type not in q.allThreadTypes:
                returnValue.append("ERR_TYPE")
            else:
                # Finding 1: Robust size resolution (handles integers and formatted floats)
                all_sizes = q.allSizes(t_type)
                target_size = str(params['size'])
                if target_size not in all_sizes:
                    try:
                        # Fallback for metric profiles: try "10.0" format
                        target_size = "{:.1f}".format(float(params['size']))
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
                        
                        # Finding 4: Detect internal/external based on normal
                        # If normal points towards axis, it's internal
                        (res, sp) = face.evaluator.getPointAtParameter(adsk.core.Point2D.create(0.5, 0.5))
                        (res, normal) = face.evaluator.getNormalAtPoint(sp)
                        axis_pt = face.geometry.origin
                        vec_to_axis = axis_pt.asVector()
                        vec_to_axis.subtract(sp.asVector())
                        is_internal = normal.dotProduct(vec_to_axis) > 0
                        
                        # Finding 1 & 3: Use ThreadInfo.create (Internal API path)
                        # Signature: isTapered, isInternal, threadType, threadDesignation, threadClass, isRightHanded
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
        
        if val.startswith("ERR_"):
            err_map = {
                "ERR_BODY": ("Körper nicht gefunden.", "Body not found."),
                "ERR_FACE": ("Zylinderfläche nicht gefunden.", "No cylindrical face found."),
                "ERR_TYPE": ("Gewindetyp nicht gefunden.", "Thread type not found."),
                "ERR_SIZE": ("Größe nicht gefunden.", "Size not found."),
                "ERR_DESIG": ("Bezeichnung nicht gefunden.", "Designation not found."),
                "ERR_UNKNOWN": ("Ein unbekannter Fehler ist aufgetreten.", "An unknown error occurred.")
            }
            msg = err_map.get(val, (val, val))
            return format_response(lang, msg[0], msg[1])
        
        return format_response(lang, f"Gewinde '{val}' angewendet.", f"Thread '{val}' applied.")
    except FusionBridgeError as e: return f"Error: {str(e)}"

def register_thread_tools(mcp):
    # Registration logic using bilingual wrappers
    mcp.tool(name="gewinde_anwenden", description="Wendet ein metrisches Gewinde auf einen Körper an.")(lambda koerper_name, gewinde_typ, groesse, bezeichnung, klasse="", modelliert=True: apply_custom_thread_logic(koerper_name, gewinde_typ, groesse, bezeichnung, klasse, modelliert, "de"))
    mcp.tool(name="apply_custom_thread", description="Applies a specific thread to a body.")(lambda body_name, thread_type, size, designation, thread_class="", is_modeled=True: apply_custom_thread_logic(body_name, thread_type, size, designation, thread_class, is_modeled, "en"))
