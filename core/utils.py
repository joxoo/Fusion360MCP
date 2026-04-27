import json
import os
import functools
import inspect

# Common Fusion 360 script fragments
COMMON_FUSION_SCRIPTS = {
    "find_body": """
import unicodedata
def normalize_name(name):
    if not name: return ""
    return " ".join(unicodedata.normalize('NFKC', str(name)).casefold().strip().split())

def ascii_fold_name(name):
    return ''.join(ch for ch in unicodedata.normalize('NFKD', normalize_name(name)) if not unicodedata.combining(ch))

def names_match(left, right):
    norm_left = normalize_name(left)
    norm_right = normalize_name(right)
    if norm_left == norm_right:
        return True
    return ascii_fold_name(left) == ascii_fold_name(right)

def find_body_recursive(component, target_name):
    for b in component.bRepBodies:
        if not target_name or names_match(b.name, target_name): return b
    for occ in component.occurrences:
        res = find_body_recursive(occ.component, target_name)
        if res: return res
    return None

def find_sketch_recursive(component, target_name):
    for s in component.sketches:
        if not target_name or names_match(s.name, target_name): return s
    for occ in component.occurrences:
        res = find_sketch_recursive(occ.component, target_name)
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
    
    # Register the original function directly. 
    # This allows FastMCP to correctly inspect type hints and default values.
    mcp.tool(name=tool_key, description=desc)(func)
