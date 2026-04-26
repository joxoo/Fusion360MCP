def build_create_loft_script() -> str:
    return """try:
    profiles = []
    for name in params['sketch_names']:
        sk = next((s for s in root.sketches if s.name == name), None)
        if sk and sk.profiles.count > 0:
            profiles.append(sk.profiles.item(0))
    
    if len(profiles) < 2:
        returnValue.append("ERR_MIN_PROFILES")
    else:
        lofts = root.features.loftFeatures
        loft_in = lofts.createInput(adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
        for p in profiles:
            loft_in.loftSections.add(p)
        loft_feat = lofts.add(loft_in)
        returnValue.append(loft_feat.bodies.item(0).name)
except Exception as e:
    returnValue.append(f"ERR_API:{str(e)}")"""


def build_create_sweep_script() -> str:
    return """try:
    prof_sk = next((s for s in root.sketches if s.name == params['profile_sketch']), None)
    path_sk = next((s for s in root.sketches if s.name == params['path_sketch']), None)
    
    if prof_sk and path_sk and prof_sk.profiles.count > 0 and path_sk.sketchCurves.count > 0:
        prof = prof_sk.profiles.item(0)
        # Use first curve as path for simplicity
        path = root.features.createPath(path_sk.sketchCurves.item(0))
        sweeps = root.features.sweepFeatures
        sweep_in = sweeps.createInput(prof, path, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
        sweep_feat = sweeps.add(sweep_in)
        returnValue.append(sweep_feat.bodies.item(0).name)
    else:
        returnValue.append("ERR_INPUT_NOT_FOUND")
except Exception as e:
    returnValue.append(f"ERR_API:{str(e)}")"""


def build_measure_distance_script() -> str:
    return """try:
    # This is a complex one, simplified: measure between two named bodies
    b1 = find_body_recursive(root, params['body1'])
    b2 = find_body_recursive(root, params['body2'])
    if b1 and b2:
        meas = app.measureManager
        res = meas.measure(b1, b2)
        returnValue.append(f"{res.value:.4f}")
    else:
        returnValue.append("ERR_BODY")
except Exception as e:
    returnValue.append(f"ERR_API:{str(e)}")"""


def build_get_center_of_mass_script() -> str:
    return """try:
    target = find_body_recursive(root, params['body'])
    if target:
        com = target.physicalProperties.centerOfMass
        returnValue.append(f"{com.x:.4f},{com.y:.4f},{com.z:.4f}")
    else:
        returnValue.append("ERR_BODY")
except Exception as e:
    returnValue.append(f"ERR_API:{str(e)}")"""


def build_apply_appearance_script() -> str:
    return """try:
    target = find_body_recursive(root, params['body'])
    lib = app.materialLibraries.itemByName('Fusion 360 Appearance Library')
    app_lib = lib.appearances.itemByName(params['appearance'])
    if target and app_lib:
        target.appearance = app_lib
        returnValue.append("OK")
    else:
        returnValue.append("ERR_NOT_FOUND")
except Exception as e:
    returnValue.append(f"ERR_API:{str(e)}")"""


def build_export_step_script() -> str:
    return """import adsk.core, adsk.fusion, os, tempfile
try:
    design = adsk.fusion.Design.cast(app.activeProduct)
    exportMgr = design.exportManager
    name = params.get('filename', 'model')
    if not name.endswith('.step'): name += '.step'
    path = os.path.expanduser("~/Downloads")
    if not os.path.exists(path): path = tempfile.gettempdir()
    full_path = os.path.join(path, name)
    options = exportMgr.createSTEPExportOptions(full_path)
    exportMgr.execute(options)
    returnValue.append(f"Exported to {full_path}")
except Exception as e:
    returnValue.append(f"Error: {str(e)}")"""
