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
    "setup_standard": """import adsk.core, adsk.fusion, traceback, math
d = adsk.fusion.Design.cast(app.activeProduct)
root = d.rootComponent"""
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

def register_tool(mcp, tool_key, func):
    """
    Register a tool with the MCP server using its canonical name.
    """
    i18n = load_i18n()
    
    # Always use the English description for the MCP schema
    en_config = i18n.get("en", {}).get("tools", {}).get(tool_key, {})
    desc = en_config.get("description", func.__doc__ or "")
    
    # We wrap the function to:
    # 1. Provide a default 'lang' if not provided by the client
    # 2. Be robust against extra arguments (like wait_for_previous) via **kwargs
    @functools.wraps(func)
    def wrapper(**kwargs):
        # Determine the target language (default to English)
        lang = kwargs.pop('lang', 'en')
        
        # Filter kwargs to only include what the original function actually accepts
        sig = inspect.signature(func)
        filtered_kwargs = {
            k: v for k, v in kwargs.items() 
            if k in sig.parameters
        }
        
        # If the function expects 'lang', pass it
        if 'lang' in sig.parameters:
            filtered_kwargs['lang'] = lang
            
        return func(**filtered_kwargs)
    
    # Build a clean signature for FastMCP inspection (client-facing schema)
    # We remove 'lang' from the public schema as it's usually handled internally
    orig_sig = inspect.signature(func)
    public_params = [
        p for name, p in orig_sig.parameters.items() 
        if name != 'lang'
    ]
    
    wrapper.__signature__ = orig_sig.replace(parameters=public_params)
    wrapper.__annotations__ = {
        k: v for k, v in func.__annotations__.items() 
        if k != 'lang'
    }
    
    # Register under the canonical tool_key (e.g., 'create_box')
    mcp.tool(name=tool_key, description=desc)(wrapper)
