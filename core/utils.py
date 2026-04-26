import json
import os
import functools
import inspect

# Common Fusion 360 script fragments
COMMON_FUSION_SCRIPTS = {
    "find_body": """
def find_body_recursive(component, target_name):
    for b in component.bRepBodies:
        if b.name == target_name or not target_name: return b
    for occ in component.occurrences:
        res = find_body_recursive(occ.component, target_name)
        if res: return res
    return None
""",
    "find_comp": """
def find_comp_recursive(root_comp, target_name):
    if target_name == "Root": return root_comp
    for occ in root_comp.allOccurrences:
        if occ.component.name == target_name: return occ.component
    return None
""",
    "placement": """
def get_offset_plane(base_plane, offset):
    if abs(offset) <= 1e-9:
        return base_plane
    planes = root.constructionPlanes
    plane_input = planes.createInput()
    plane_input.setByOffset(base_plane, adsk.core.ValueInput.createByReal(offset))
    return planes.add(plane_input)

def translate_body(body, x=0.0, y=0.0, z=0.0):
    if abs(x) <= 1e-9 and abs(y) <= 1e-9 and abs(z) <= 1e-9:
        return body
    entities = adsk.core.ObjectCollection.create()
    entities.add(body)
    move_feats = root.features.moveFeatures
    move_input = move_feats.createInput2(entities)
    move_input.defineAsTranslateXYZ(
        adsk.core.ValueInput.createByReal(x),
        adsk.core.ValueInput.createByReal(y),
        adsk.core.ValueInput.createByReal(z),
        True
    )
    move_feats.add(move_input)
    return body
""",
    "setup_standard": """
import adsk.core, adsk.fusion, traceback, math
d = adsk.fusion.Design.cast(app.activeProduct)
root = d.rootComponent
"""
}

_I18N_DATA = None

def load_i18n(file_path=None):
    global _I18N_DATA
    if _I18N_DATA is not None:
        return _I18N_DATA
    if file_path is None:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        file_path = os.path.join(base_dir, "i18n.json")
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            _I18N_DATA = json.load(f)
            return _I18N_DATA
    except Exception:
        _I18N_DATA = {"de": {}, "en": {}}
        return _I18N_DATA

def format_response(lang, key, **kwargs):
    i18n = load_i18n()
    message = i18n.get(lang, {}).get("messages", {}).get(key)
    if message is None:
        message = i18n.get(lang, {}).get("errors", {}).get(key, key)
    try:
        return message.format(**kwargs)
    except Exception:
        return message

def register_tool(mcp, tool_key, func, param_aliases=None):
    """
    Simpler registration that uses FastMCP native tool decorator.
    """
    i18n = load_i18n()

    # Define wrappers for each language
    for lang in ("de", "en"):
        config = i18n.get(lang, {}).get("tools", {}).get(tool_key)
        if not config: continue
        
        name = config.get("name")
        desc = config.get("description", "")
        alias_map = config.get("param_aliases", {})
        
        if name:
            # We create a specific function for FastMCP to inspect
            # This function must match the canonical logic but with localized names
            
            orig_sig = inspect.signature(func)
            params = [p for n, p in orig_sig.parameters.items() if n != 'lang']
            
            # Map parameters to localized names
            loc_params = []
            for p in params:
                loc_name = alias_map.get(p.name, p.name)
                loc_params.append(p.replace(name=loc_name))
            
            new_sig = orig_sig.replace(parameters=loc_params)

            def create_closure(target_lang, local_alias_map):
                reverse_map = {v: k for k, v in local_alias_map.items()}
                
                @functools.wraps(func)
                def tool_func(**kwargs):
                    # Map back to canonical
                    canonical_kwargs = {reverse_map.get(k, k): v for k, v in kwargs.items()}
                    return func(lang=target_lang, **canonical_kwargs)
                
                # Re-apply the localized signature and annotations so FastMCP sees them
                tool_func.__signature__ = new_sig
                tool_func.__annotations__ = {alias_map.get(k, k): v for k, v in func.__annotations__.items() if k != 'lang'}
                return tool_func

            mcp.tool(name=name, description=desc)(create_closure(lang, alias_map))
