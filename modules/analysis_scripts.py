def build_get_volumetric_properties_script() -> str:
    return """import json
try:
    target = find_body_recursive(root, params['body'])
    if target:
        props = target.physicalProperties
        # Moments of Inertia returns (success, ixx, iyy, izz, ixy, iyz, ixz)
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
        # Create interference input
        design = adsk.fusion.Design.cast(app.activeProduct)
        int_input = design.createInterferenceInput(bodies)
        int_input.areCoincidentFacesIncluded = params.get('include_coincident', False)
        
        # Analyze
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
        # Convert degrees to radians
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


def build_analyze_bodies_script() -> str:
    return """import json
try:
    bodies_info = []
    for b in root.bRepBodies:
        bodies_info.append({
            "name": b.name,
            "volume": b.volume,
            "area": b.area,
            "visible": b.isVisible
        })
    returnValue.append(json.dumps(bodies_info))
except Exception as e:
    returnValue.append(f"Error: {str(e)}")"""
