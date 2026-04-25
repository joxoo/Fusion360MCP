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

def _build_localized_signature(func, alias_map):
    sig = inspect.signature(func)
    localized_params = []
    reverse_alias_map = {}

    for param in sig.parameters.values():
        if param.name == "lang":
            continue
        localized_name = alias_map.get(param.name, param.name)
        reverse_alias_map[localized_name] = param.name
        localized_params.append(param.replace(name=localized_name))

    return sig.replace(parameters=localized_params), reverse_alias_map

def register_tool(mcp, tool_key, func, param_aliases=None):
    """
    Registers a tool for both German and English if defined in i18n.json.
    Supports localized parameter names through i18n metadata or explicit aliases.
    """
    i18n = load_i18n()

    def create_wrapper(target_lang, config):
        alias_map = {}
        if config:
            alias_map.update(config.get("param_aliases", {}))
        if param_aliases:
            alias_map.update(param_aliases.get(target_lang, {}))

        localized_sig, reverse_alias_map = _build_localized_signature(func, alias_map)

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            bound = localized_sig.bind_partial(*args, **kwargs)
            canonical_kwargs = {
                reverse_alias_map.get(name, name): value
                for name, value in bound.arguments.items()
            }
            return func(lang=target_lang, **canonical_kwargs)
        wrapper.__signature__ = localized_sig
        return wrapper

    for lang in ("de", "en"):
        config = i18n.get(lang, {}).get("tools", {}).get(tool_key)
        if not config:
            continue
        name = config.get("name")
        desc = config.get("description", "")
        if name:
            mcp.tool(name=name, description=desc)(create_wrapper(lang, config))
