def build_manage_parameter_script() -> str:
    return """try:
    params_coll = d.userParameters
    existing = params_coll.itemByName(params['name'])
    if existing:
        existing.expression = params['expr']
        returnValue.append("UPDATED")
    else:
        val = adsk.core.ValueInput.createByString(params['expr'])
        params_coll.add(params['name'], val, params['unit'], params['comment'])
        returnValue.append("CREATED")
except Exception as e:
    returnValue.append(f"ERR_API:{str(e)}")"""
