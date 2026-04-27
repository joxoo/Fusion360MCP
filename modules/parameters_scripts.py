def build_list_parameters_script() -> str:
    return """import json
try:
    p_coll = d.userParameters
    params_info = []
    for p in p_coll:
        params_info.append({
            "name": p.name,
            "expression": p.expression,
            "value": p.value,
            "unit": p.unit,
            "comment": p.comment
        })
    returnValue.append(json.dumps(params_info))
except Exception as e:
    returnValue.append(f"ERR_API:{str(e)}")"""


def build_delete_parameter_script() -> str:
    return """try:
    p_coll = d.userParameters
    target = p_coll.itemByName(params['name'])
    if target:
        try:
            target.deleteMe()
            returnValue.append("OK")
        except:
            returnValue.append("ERR_IN_USE")
    else:
        returnValue.append("ERR_NOT_FOUND")
except Exception as e:
    returnValue.append(f"ERR_API:{str(e)}")"""


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
