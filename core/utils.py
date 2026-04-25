import json
import os
import functools
import inspect

# Common Fusion 360 script fragments (Python code executed inside Fusion)
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
    "setup_standard": """
import adsk.core, adsk.fusion, traceback, math
d = adsk.fusion.Design.cast(app.activeProduct)
root = d.rootComponent
"""
}

# Global I18N data
_I18N_DATA = None

def load_i18n(file_path=None):
    global _I18N_DATA
    if _I18N_DATA is not None:
        return _I18N_DATA
    
    if file_path is None:
        # Default path relative to this file
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
    """Formats return messages based on the requested language and a key in i18n.json."""
    i18n = load_i18n()
    
    # Try messages first
    message = i18n.get(lang, {}).get("messages", {}).get(key)
    
    # If key was not in messages, check errors
    if message is None:
        message = i18n.get(lang, {}).get("errors", {}).get(key, key)
    
    try:
        return message.format(**kwargs)
    except Exception:
        return message

def register_tool(mcp, tool_key, func):
    """
    Registers a tool for both German and English if defined in i18n.json.
    Preserves the function signature while injecting the 'lang' parameter.
    """
    i18n = load_i18n()
    
    de = i18n.get("de", {}).get("tools", {}).get(tool_key)
    en = i18n.get("en", {}).get("tools", {}).get(tool_key)
    
    # Get original signature
    sig = inspect.signature(func)
    params = list(sig.parameters.values())
    # Create new signature without 'lang'
    params_no_lang = [p for p in params if p.name != 'lang']
    new_sig = sig.replace(parameters=params_no_lang)

    def create_wrapper(target_lang):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, lang=target_lang, **kwargs)
        wrapper.__signature__ = new_sig
        return wrapper

    if de:
        name = de.get("name")
        desc = de.get("description", "")
        if name:
            mcp.tool(name=name, description=desc)(create_wrapper("de"))
                
    if en:
        name = en.get("name")
        desc = en.get("description", "")
        if name:
            mcp.tool(name=name, description=desc)(create_wrapper("en"))
