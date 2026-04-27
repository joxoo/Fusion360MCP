import json
import os
import functools
import inspect

IGNORED_TOOL_KWARGS = {"wait_for_previous"}

TOOL_ALIASES = {
    "create_new_design": ["neue_konstruktion"],
    "cleanup_design": ["design_bereinigen"],
    "create_box": ["box_erstellen"],
    "create_sketch": ["skizze_erstellen"],
    "sketch_polygon": ["polygon_zeichnen", "draw_polygon"],
    "draw_circle": ["kreis_zeichnen"],
    "get_body_info": ["koerper_analysieren"],
}

PARAM_ALIASES = {
    "create_sketch": {
        "plane": "plane_name",
        "ebene": "plane_name",
    },
    "sketch_polygon": {
        "skizzen_name": "sketch_name",
        "center_x": "cx",
        "center_y": "cy",
        "seiten": "sides",
    },
    "draw_circle": {
        "skizzen_name": "sketch_name",
        "center_x": "x",
        "center_y": "y",
    },
}

ALIAS_SIGNATURES = {
    "skizze_erstellen": {
        "ebene": "plane_name",
        "name": "name",
    },
    "polygon_zeichnen": {
        "skizzen_name": "sketch_name",
        "center_x": "cx",
        "center_y": "cy",
        "radius": "radius",
        "seiten": "sides",
    },
    "draw_polygon": {
        "sketch_name": "sketch_name",
        "center_x": "cx",
        "center_y": "cy",
        "radius": "radius",
        "sides": "sides",
    },
    "kreis_zeichnen": {
        "skizzen_name": "sketch_name",
        "center_x": "x",
        "center_y": "y",
        "radius": "radius",
    },
}

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

def find_tspline_body_recursive(component, target_name):
    form_features = getattr(component.features, 'formFeatures', None)
    if form_features:
        for i in range(form_features.count):
            form_feature = form_features.item(i)
            ts_bodies = getattr(form_feature, 'tSplineBodies', None)
            if not ts_bodies:
                continue
            for j in range(ts_bodies.count):
                ts_body = ts_bodies.item(j)
                if not target_name or names_match(ts_body.name, target_name):
                    return ts_body
    for occ in component.occurrences:
        res = find_tspline_body_recursive(occ.component, target_name)
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
root = d.rootComponent
active_comp = d.activeComponent or root

def get_target_comp():
    return d.activeComponent or root
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

def register_tool(mcp, tool_key, func):
    """
    Register a tool with the MCP server using its canonical name.
    """
    i18n = load_i18n()
    
    # Always use the English description for the MCP schema
    en_config = i18n.get("en", {}).get("tools", {}).get(tool_key, {})
    desc = en_config.get("description", func.__doc__ or "")
    
    sig = inspect.signature(func)
    accepted_params = set(sig.parameters.keys())
    alias_map = PARAM_ALIASES.get(tool_key, {})

    is_async = inspect.iscoroutinefunction(func)

    if is_async:
        @functools.wraps(func)
        async def wrapper(**kwargs):
            normalized = {}
            for key, value in kwargs.items():
                if key in IGNORED_TOOL_KWARGS:
                    continue
                canonical_key = alias_map.get(key, key)
                if canonical_key in accepted_params:
                    normalized[canonical_key] = value

            if "lang" in sig.parameters:
                normalized.setdefault("lang", "en")

            return await func(**normalized)
    else:
        @functools.wraps(func)
        def wrapper(**kwargs):
            normalized = {}
            for key, value in kwargs.items():
                if key in IGNORED_TOOL_KWARGS:
                    continue
                canonical_key = alias_map.get(key, key)
                if canonical_key in accepted_params:
                    normalized[canonical_key] = value

            if "lang" in sig.parameters:
                normalized.setdefault("lang", "en")

            return func(**normalized)

    public_params = [
        param for name, param in sig.parameters.items()
        if name != "lang"
    ]
    wrapper.__signature__ = sig.replace(parameters=public_params)
    wrapper.__annotations__ = {
        key: value for key, value in func.__annotations__.items()
        if key != "lang"
    }

    mcp.tool(name=tool_key, description=desc)(wrapper)

    for alias in TOOL_ALIASES.get(tool_key, []):
        alias_wrapper = wrapper
        alias_signature_map = ALIAS_SIGNATURES.get(alias)
        if alias_signature_map:
            alias_parameters = []
            for alias_param_name, canonical_param_name in alias_signature_map.items():
                canonical_param = sig.parameters[canonical_param_name]
                alias_parameters.append(
                    inspect.Parameter(
                        alias_param_name,
                        kind=canonical_param.kind,
                        default=canonical_param.default,
                        annotation=canonical_param.annotation,
                    )
                )
            
            if is_async:
                async def async_alias_wrapper(**kwargs):
                    return await wrapper(**kwargs)
                alias_wrapper = functools.wraps(func)(async_alias_wrapper)
            else:
                alias_wrapper = functools.wraps(func)(lambda **kwargs: wrapper(**kwargs))
                
            alias_wrapper.__signature__ = sig.replace(parameters=alias_parameters)
            alias_wrapper.__annotations__ = {
                alias_name: sig.parameters[canonical_name].annotation
                for alias_name, canonical_name in alias_signature_map.items()
            }
        else:
            if is_async:
                async def async_simple_alias_wrapper(**kwargs):
                    return await wrapper(**kwargs)
                alias_wrapper = functools.wraps(func)(async_simple_alias_wrapper)
            else:
                alias_wrapper = wrapper

        mcp.tool(name=alias, description=desc)(alias_wrapper)
