def build_create_loft_script() -> str:
    return """try:
    sketches, owner_comp, err = resolve_multi_sketch_context(
        params['sketch_names'],
        params.get('component_name'),
        params.get('component_path')
    )
    if err == "ERR_COMPONENT":
        returnValue.append("ERR_COMPONENT")
    elif err == "ERR_OWNER_MISMATCH":
        returnValue.append("ERR_OWNER_MISMATCH")
    else:
        profiles = []
        for sk in sketches:
            if sk and sk.profiles.count > 0:
                profiles.append(sk.profiles.item(0))

        if len(profiles) < 2:
            returnValue.append("ERR_MIN_PROFILES")
        else:
            lofts = owner_comp.features.loftFeatures
            loft_in = lofts.createInput(adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
            for p in profiles:
                loft_in.loftSections.add(p)
            
            # Advanced: Centerline support
            if 'centerline_sketch' in params:
                cl_sk, _, cl_err = resolve_sketch_context(params['centerline_sketch'], params.get('component_name'), params.get('component_path'))
                if cl_sk and cl_sk.sketchCurves.count > 0:
                    path = owner_comp.features.createPath(cl_sk.sketchCurves.item(0))
                    loft_in.centerLineOrRails.addCenterLine(path)
            
            loft_feat = lofts.add(loft_in)
            returnValue.append(loft_feat.bodies.item(0).name)
except Exception as e:
    returnValue.append(f"ERR_API:{str(e)}")"""


def build_create_sweep_script() -> str:
    return """try:
    prof_sk, owner_comp, profile_err = resolve_sketch_context(
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
    elif prof_sk and path_sk and owner_comp != path_owner:
        returnValue.append("ERR_OWNER_MISMATCH")
    elif prof_sk and path_sk and prof_sk.profiles.count > 0 and path_sk.sketchCurves.count > 0:
        prof = prof_sk.profiles.item(0)
        path = owner_comp.features.createPath(path_sk.sketchCurves.item(0))
        sweeps = owner_comp.features.sweepFeatures
        
        # Advanced: Taper and Twist
        taper = adsk.core.ValueInput.createByReal(params.get('taper', 0))
        twist = adsk.core.ValueInput.createByReal(params.get('twist', 0))
        
        sweep_in = sweeps.createInput(prof, path, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
        sweep_in.taperAngle = taper
        sweep_in.twistAngle = twist
        
        sweep_feat = sweeps.add(sweep_in)
        returnValue.append(sweep_feat.bodies.item(0).name)
    else:
        returnValue.append("ERR_INPUT_NOT_FOUND")
except Exception as e:
    returnValue.append(f"ERR_API:{str(e)}")"""


def build_create_revolve_script() -> str:
    return """try:
    prof_sk, owner_comp, profile_err = resolve_sketch_context(
        params['profile_sketch'],
        params.get('component_name'),
        params.get('component_path')
    )
    if profile_err == "ERR_COMPONENT":
        returnValue.append("ERR_COMPONENT")
    elif prof_sk and prof_sk.profiles.count > 0:
        prof = prof_sk.profiles.item(0)
        
        # Axis can be a sketch line or construction axis
        axis_entity = None
        if 'axis_sketch' in params:
            ax_sk, _, _ = resolve_sketch_context(params['axis_sketch'], params.get('component_name'), params.get('component_path'))
            if ax_sk and ax_sk.sketchCurves.sketchLines.count > 0:
                axis_entity = ax_sk.sketchCurves.sketchLines.item(0)
        
        if not axis_entity:
            axis_name = params.get('axis', 'z')
            if axis_name.lower() == 'x': axis_entity = owner_comp.xConstructionAxis
            elif axis_name.lower() == 'y': axis_entity = owner_comp.yConstructionAxis
            else: axis_entity = owner_comp.zConstructionAxis
            
        angle = adsk.core.ValueInput.createByReal(params.get('angle', 6.283185)) # Default 360 deg
        revolves = owner_comp.features.revolveFeatures
        rev_in = revolves.createInput(prof, axis_entity, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
        rev_in.setAngleExtent(False, angle)
        rev_feat = revolves.add(rev_in)
        returnValue.append(rev_feat.bodies.item(0).name)
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
