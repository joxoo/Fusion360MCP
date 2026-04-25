from core.bridge import execute_fusion_script, get_i18n_data, FusionBridgeError
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
I18N_PATH = os.path.join(BASE_DIR, "i18n.json")
I18N = get_i18n_data(I18N_PATH)

def apply_custom_thread_logic(body_name: str, thread_type: str, size: str, designation: str, thread_class: str, is_modeled: bool):
    script = """
import adsk.core, adsk.fusion
try:
    d = adsk.fusion.Design.cast(app.activeProduct)
    c = d.rootComponent
    
    def find_cylindrical_face_recursive(component, target_body_name):
        # 1. Suche in den Koerpern dieser Komponente
        for b in component.bRepBodies:
            if b.name == target_body_name or not target_body_name:
                face = next((f for f in b.faces if f.geometry.objectType == adsk.core.Cylinder.classType()), None)
                if face: return face
        
        # 2. Rekursiv in Unter-Komponenten (Occurrences) suchen
        for occ in component.occurrences:
            face = find_cylindrical_face_recursive(occ.component, target_body_name)
            if face: return face
        return None

    target_face = find_cylindrical_face_recursive(c, params['body_name'])
    
    if not target_face:
        msg = f"Error: No cylindrical face found on body '{params['body_name']}'." if params['body_name'] else "Error: No cylindrical face found in assembly."
        returnValue.append(msg)
    else:
        q = adsk.fusion.ThreadDataQuery.create()
        t_type = params['thread_type']
        
        # Validation
        all_types = q.allThreadTypes
        if t_type not in all_types:
            returnValue.append(f"Error: Thread type '{t_type}' not found. Available: {', '.join(all_types)}")
        else:
            sizes = q.allSizes(t_type)
            target_size = params['size']
            if target_size not in sizes:
                returnValue.append(f"Error: Size '{target_size}' not found for type '{t_type}'. Available: {', '.join(sizes)}")
            else:
                desigs = q.allDesignations(t_type, target_size)
                target_desig = params['designation']
                if target_desig not in desigs:
                    returnValue.append(f"Error: Designation '{target_desig}' not found. Available: {', '.join(desigs)}")
                else:
                    classes = q.allClasses(False, t_type, target_desig)
                    target_class = params['thread_class']
                    if target_class and target_class not in classes:
                        returnValue.append(f"Error: Class '{target_class}' not found. Available: {', '.join(classes)}")
                    else:
                        final_class = target_class if target_class else classes[0]
                        t_info = adsk.fusion.ThreadInfo.create(False, False, t_type, target_desig, final_class, True)
                        tf = target_face.body.parentComponent.features.threadFeatures
                        t_input = tf.createInput(target_face, t_info)
                        t_input.isModeled = params['is_modeled']
                        tf.add(t_input)
                        returnValue.append(f"Thread {target_desig} ({final_class}) applied to body '{target_face.body.name}'.")
except Exception as e:
    returnValue.append(f"Fatal Error: {str(e)}")
"""
    try:
        res = execute_fusion_script(script, {
            "body_name": body_name,
            "thread_type": thread_type,
            "size": size,
            "designation": designation,
            "thread_class": thread_class,
            "is_modeled": is_modeled
        })
        return res.get("data", ["Error"])[0]
    except FusionBridgeError as e:
        return str(e)

def register_thread_tools(mcp):
    # (Tools werden hier wie gewohnt registriert, nutzen aber die neue Logik)
    @mcp.tool(name="apply_custom_thread", description="Applies a specific thread to a body.")
    def apply_custom_thread(body_name: str, thread_type: str, size: str, designation: str, thread_class: str = "", is_modeled: bool = True) -> str:
        return apply_custom_thread_logic(body_name, thread_type, size, designation, thread_class, is_modeled)

    @mcp.tool(name="dump_thread_config", description="Lists available thread types and sizes.")
    def dump_thread_config() -> str:
        script = "q = adsk.fusion.ThreadDataQuery.create(); returnValue.append(','.join(q.allThreadTypes))"
        try:
            res = execute_fusion_script(script)
            return res.get("data", [""])[0]
        except FusionBridgeError as e:
            return str(e)
