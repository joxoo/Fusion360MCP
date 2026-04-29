import json

def build_get_feature_history_script() -> str:
    return """import json
try:
    design = adsk.fusion.Design.cast(app.activeProduct)
    timeline = design.timeline
    history = []
    for i in range(timeline.count):
        item = timeline.item(i)
        feat_type = "Unknown"
        try:
            if item.entity:
                feat_type = item.entity.objectType.split('::')[-1]
        except: pass
        
        history.append({
            "index": i,
            "name": item.name,
            "feature_type": feat_type,
            "is_suppressed": item.isSuppressed,
            "is_rolled_back": i >= timeline.markerPosition
        })
    returnValue.append(json.dumps(history))
except Exception as e:
    returnValue.append(f"ERR_API:{str(e)}")"""


def build_get_volumetric_properties_script() -> str:
    return """import json
try:
    target = find_body_recursive(root, params['body'])
    if target:
        props = target.physicalProperties
        res, ixx, iyy, izz, ixy, iyz, ixz = props.getXYZMomentsOfInertia()
        
        info = {
            "name": target.name,
            "mass_kg": props.mass,
            "volume_cm3": props.volume,
            "density_kg_cm3": props.density,
            "area_cm2": props.area,
            "moments_of_inertia": {
                "ixx": ixx, "iyy": iyy, "izz": izz,
                "ixy": ixy, "iyz": iyz, "ixz": ixz
            }
        }
        returnValue.append(json.dumps(info))
    else:
        returnValue.append("ERR_BODY")
except Exception as e:
    returnValue.append(f"ERR_API:{str(e)}")"""


def build_get_bounding_box_script() -> str:
    return """import json
try:
    target = find_body_recursive(root, params['body'])
    if target:
        bbox = target.boundingBox
        min_pt = bbox.minPoint
        max_pt = bbox.maxPoint
        
        info = {
            "name": target.name,
            "min_x": min_pt.x, "min_y": min_pt.y, "min_z": min_pt.z,
            "max_x": max_pt.x, "max_y": max_pt.y, "max_z": max_pt.z,
            "length": max_pt.x - min_pt.x,
            "width": max_pt.y - min_pt.y,
            "height": max_pt.z - min_pt.z
        }
        returnValue.append(json.dumps(info))
    else:
        returnValue.append("ERR_BODY")
except Exception as e:
    returnValue.append(f"ERR_API:{str(e)}")"""


def build_check_interference_script() -> str:
    return """try:
    bodies = adsk.core.ObjectCollection.create()
    for name in params['body_names']:
        b = find_body_recursive(root, name)
        if b: bodies.add(b)
    
    if bodies.count > 1:
        design = adsk.fusion.Design.cast(app.activeProduct)
        int_input = design.createInterferenceInput(bodies)
        int_input.areCoincidentFacesIncluded = params.get('include_coincident', False)
        results = design.analyzeInterference(int_input)
        returnValue.append(str(results.count))
    else:
        returnValue.append("ERR_MIN_BODIES")
except Exception as e:
    returnValue.append(f"ERR_API:{str(e)}")"""


def build_create_draft_analysis_script() -> str:
    return """try:
    target = find_body_recursive(root, params['body'])
    if target:
        pull_dir = root.zConstructionAxis
        analyses = root.analyses
        min_angle = params.get('min_angle', 0.5) * (3.14159 / 180.0)
        max_angle = params.get('max_angle', 5.0) * (3.14159 / 180.0)
        
        d_in = analyses.createDraftAnalysisInput(target, pull_dir, min_angle, max_angle, True)
        d_feat = analyses.add(d_in)
        d_feat.name = f"Draft_{target.name}"
        returnValue.append(d_feat.name)
    else:
        returnValue.append("ERR_BODY")
except Exception as e:
    returnValue.append(f"ERR_API:{str(e)}")"""


def build_capture_view_script() -> str:
    return """import base64, os, tempfile
try:
    view = app.activeViewport
    temp_dir = tempfile.gettempdir()
    file_path = os.path.join(temp_dir, 'fusion_screenshot.png')
    view.saveAsImageFile(file_path, 0, 0)
    with open(file_path, 'rb') as f:
        encoded = base64.b64encode(f.read()).decode('utf-8')
    os.remove(file_path)
    returnValue.append(encoded)
except Exception as e:
    returnValue.append(f"Error: {str(e)}")"""


def build_capture_standard_views_script() -> str:
    return """import base64, os, tempfile, json
try:
    vp = app.activeViewport
    cam = vp.camera
    temp_dir = tempfile.gettempdir()
    results = {}
    
    views = [
        ("top", adsk.core.ViewOrientations.TopViewOrientation),
        ("front", adsk.core.ViewOrientations.FrontViewOrientation),
        ("right", adsk.core.ViewOrientations.RightViewOrientation),
        ("iso", adsk.core.ViewOrientations.IsoTopRightViewOrientation)
    ]
    
    for name, orient in views:
        cam.viewOrientation = orient
        cam.isFitView = True
        vp.camera = cam
        vp.refresh()
        adsk.doEvents()
        
        path = os.path.join(temp_dir, f"cap_{name}.png")
        vp.saveAsImageFile(path, 800, 600)
        with open(path, "rb") as f:
            results[name] = base64.b64encode(f.read()).decode('utf-8')
        os.remove(path)
            
    returnValue.append(json.dumps(results))
except Exception as e:
    returnValue.append(f"ERR_API:{str(e)}")"""


def build_analyze_bodies_script() -> str:
    return """import json
try:
    bodies_info = []
    for b in root.bRepBodies:
        bodies_info.append({
            "name": b.name,
            "type": "BRep",
            "volume": b.volume,
            "area": b.area,
            "visible": b.isVisible
        })
    for m in root.meshBodies:
        bodies_info.append({
            "name": m.name,
            "type": "Mesh",
            "visible": m.isVisible
        })
    returnValue.append(json.dumps(bodies_info))
except Exception as e:
    returnValue.append(f"Error: {str(e)}")"""


def build_get_scene_map_script() -> str:
    return """import json
try:
    scene_map = []
    def collect_bodies(comp):
        # BReps
        for b in comp.bRepBodies:
            bbox = b.boundingBox
            try:
                center = b.physicalProperties.centerOfMass
                cx, cy, cz = center.x, center.y, center.z
            except:
                cx, cy, cz = 0, 0, 0
                
            scene_map.append({
                "name": b.name,
                "type": "BRep",
                "center": {"x": cx, "y": cy, "z": cz},
                "bbox": {
                    "min": {"x": bbox.minPoint.x, "y": bbox.minPoint.y, "z": bbox.minPoint.z},
                    "max": {"x": bbox.maxPoint.x, "y": bbox.maxPoint.y, "z": bbox.maxPoint.z},
                    "size": {"l": bbox.maxPoint.x - bbox.minPoint.x, "w": bbox.maxPoint.y - bbox.minPoint.y, "h": bbox.maxPoint.z - bbox.minPoint.z}
                },
                "is_visible": b.isVisible
            })
        # Meshes
        for m in comp.meshBodies:
            bbox = m.boundingBox
            scene_map.append({
                "name": m.name,
                "type": "Mesh",
                "bbox": {
                    "min": {"x": bbox.minPoint.x, "y": bbox.minPoint.y, "z": bbox.minPoint.z},
                    "max": {"x": bbox.maxPoint.x, "y": bbox.maxPoint.y, "z": bbox.maxPoint.z},
                    "size": {"l": bbox.maxPoint.x - bbox.minPoint.x, "w": bbox.maxPoint.y - bbox.minPoint.y, "h": bbox.maxPoint.z - bbox.minPoint.z}
                },
                "is_visible": m.isVisible
            })
        for occ in comp.occurrences:
            collect_bodies(occ.component)

    collect_bodies(root)
    returnValue.append(json.dumps(scene_map))
except Exception as e:
    returnValue.append(f"ERR_API:{str(e)}")"""


def build_validate_model_script() -> str:
    return """import json
try:
    results = {
        "brep_count": 0,
        "mesh_count": 0,
        "bodies": [],
        "manifold_issues": []
    }
    
    def validate_comp(comp):
        for b in comp.bRepBodies:
            results["brep_count"] += 1
            results["bodies"].append({"name": b.name, "type": "BRep", "is_solid": b.isSolid})
            if not b.isSolid:
                results["manifold_issues"].append(f"BRep '{b.name}' in {comp.name} is open.")

        for m in comp.meshBodies:
            results["mesh_count"] += 1
            results["bodies"].append({"name": m.name, "type": "Mesh"})
            
        for occ in comp.occurrences:
            validate_comp(occ.component)

    validate_comp(root)
    returnValue.append(json.dumps(results))
except Exception as e:
    returnValue.append(f"ERR_API:{str(e)}")"""


def build_get_assembly_tree_script() -> str:
    return """import json
def get_comp_info(comp, path):
    info = {
        "name": comp.name,
        "path": path,
        "bodies": [b.name for b in comp.bRepBodies],
        "meshes": [m.name for m in comp.meshBodies],
        "sketches": [s.name for s in comp.sketches],
        "components": []
    }
    for occ in comp.occurrences:
        child_path = f"{path}/{occ.name}"
        info["components"].append(get_comp_info(occ.component, child_path))
    return info

try:
    tree = get_comp_info(root, "Root")
    returnValue.append(json.dumps(tree))
except Exception as e:
    returnValue.append(f"ERR_API:{str(e)}")"""


def build_analyze_design_script() -> str:
    return """
import json, base64, os, tempfile
try:
    action = params.get('action', 'validate')
    def collect_scene_map(comp, scene_map):
        for b in comp.bRepBodies:
            bbox = b.boundingBox
            try:
                center = b.physicalProperties.centerOfMass
                cx, cy, cz = center.x, center.y, center.z
            except:
                cx, cy, cz = 0, 0, 0
            scene_map.append({"name": b.name, "type": "BRep", "center": {"x": cx, "y": cy, "z": cz}, "bbox": {"min": {"x": bbox.minPoint.x, "y": bbox.minPoint.y, "z": bbox.minPoint.z}, "max": {"x": bbox.maxPoint.x, "y": bbox.maxPoint.y, "z": bbox.maxPoint.z}, "size": {"l": bbox.maxPoint.x - bbox.minPoint.x, "w": bbox.maxPoint.y - bbox.minPoint.y, "h": bbox.maxPoint.z - bbox.minPoint.z}}, "is_visible": b.isVisible})
        for m in comp.meshBodies:
            bbox = m.boundingBox
            scene_map.append({"name": m.name, "type": "Mesh", "bbox": {"min": {"x": bbox.minPoint.x, "y": bbox.minPoint.y, "z": bbox.minPoint.z}, "max": {"x": bbox.maxPoint.x, "y": bbox.maxPoint.y, "z": bbox.maxPoint.z}, "size": {"l": bbox.maxPoint.x - bbox.minPoint.x, "w": bbox.maxPoint.y - bbox.minPoint.y, "h": bbox.maxPoint.z - bbox.minPoint.z}}, "is_visible": m.isVisible})
        for occ in comp.occurrences:
            collect_scene_map(occ.component, scene_map)

    def collect_validation(comp, results):
        for b in comp.bRepBodies:
            results["brep_count"] += 1
            results["bodies"].append({"name": b.name, "type": "BRep", "is_solid": b.isSolid})
            if not b.isSolid:
                results["manifold_issues"].append(f"BRep '{b.name}' in {comp.name} is open.")
        for m in comp.meshBodies:
            results["mesh_count"] += 1
            results["bodies"].append({"name": m.name, "type": "Mesh"})
        for occ in comp.occurrences:
            collect_validation(occ.component, results)

    if action == 'get_assembly_tree':
        def get_comp_info(comp, path):
            info = {"name": comp.name, "path": path, "bodies": [b.name for b in comp.bRepBodies], "meshes": [m.name for m in comp.meshBodies], "sketches": [s.name for s in comp.sketches], "components": []}
            for occ in comp.occurrences: info["components"].append(get_comp_info(occ.component, f"{path}/{occ.name}"))
            return info
        returnValue.append(json.dumps(get_comp_info(root, "Root")))
    elif action == 'capture_view':
        view = app.activeViewport
        path = os.path.join(tempfile.gettempdir(), 'fusion_cap.png')
        view.saveAsImageFile(path, 800, 600)
        with open(path, 'rb') as f: returnValue.append(base64.b64encode(f.read()).decode('utf-8'))
        os.remove(path)
    elif action == 'validate':
        results = {"body_count": 0, "brep_count": 0, "mesh_count": 0, "bodies": [], "manifold_issues": []}
        collect_validation(root, results)
        results["body_count"] = results["brep_count"]
        returnValue.append(json.dumps(results))
    elif action == 'scene_map':
        scene_map = []
        collect_scene_map(root, scene_map)
        returnValue.append(json.dumps(scene_map))
    elif action == 'physical_data':
        target = find_body_recursive(root, params.get('body'))
        if target:
            props = target.physicalProperties
            res, ixx, iyy, izz, ixy, iyz, ixz = props.getXYZMomentsOfInertia()
            returnValue.append(json.dumps({"name": target.name, "mass_kg": props.mass, "volume_cm3": props.volume, "density_kg_cm3": props.density, "area_cm2": props.area, "moments_of_inertia": {"ixx": ixx, "iyy": iyy, "izz": izz, "ixy": ixy, "iyz": iyz, "ixz": ixz}}))
        else: returnValue.append("ERR_BODY")
    elif action == 'bounding_box':
        target = find_body_recursive(root, params.get('body'))
        if target:
            bbox = target.boundingBox
            returnValue.append(json.dumps({"name": target.name, "min": {"x": bbox.minPoint.x, "y": bbox.minPoint.y, "z": bbox.minPoint.z}, "max": {"x": bbox.maxPoint.x, "y": bbox.maxPoint.y, "z": bbox.maxPoint.z}, "size": {"l": bbox.maxPoint.x - bbox.minPoint.x, "w": bbox.maxPoint.y - bbox.minPoint.y, "h": bbox.maxPoint.z - bbox.minPoint.z}}))
        else: returnValue.append("ERR_BODY")
    else: returnValue.append("ERR_UNKNOWN_ACTION")
except Exception as e:
    returnValue.append(f"ERR_API:{str(e)}")
"""
