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

def strip_instance_suffix(name):
    if not name: return ""
    return str(name).split(":")[0]

def names_match(left, right):
    norm_left = normalize_name(strip_instance_suffix(left))
    norm_right = normalize_name(strip_instance_suffix(right))
    if norm_left == norm_right:
        return True
    return ascii_fold_name(strip_instance_suffix(left)) == ascii_fold_name(strip_instance_suffix(right))

def find_body_recursive(component, target_name):
    if not target_name: return None
    for b in component.bRepBodies:
        if names_match(b.name, target_name): return b
    for occ in component.occurrences:
        res = find_body_recursive(occ.component, target_name)
        if res: return res
    return None

def find_sketch_recursive(component, target_name):
    if not target_name: return None
    for s in component.sketches:
        if names_match(s.name, target_name): return s
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

def get_owner_component(entity):
    owner = getattr(entity, 'parentComponent', None)
    return owner if owner else root

def get_component_name(component):
    if component == root:
        return "Root"
    return getattr(component, 'name', 'Root')

def get_component_path(component):
    if component == root:
        return "Root"
    for occ in root.allOccurrences:
        if occ.component == component:
            path = occ.fullPathName or occ.name
            return f"Root/{path}" if not str(path).startswith("Root/") else path
    return get_component_name(component)

def find_component_by_name_recursive(component, target_name):
    if not target_name:
        return component
    if names_match(get_component_name(component), target_name):
        return component
    for occ in component.occurrences:
        res = find_component_by_name_recursive(occ.component, target_name)
        if res:
            return res
    return None

def find_component_by_path(root_comp, target_path):
    if not target_path:
        return root_comp
    normalized_path = str(target_path).strip().replace("\\\\", "/")
    if normalized_path in ("Root", "/Root"):
        return root_comp

    if normalized_path.startswith("Root/"):
        normalized_path = normalized_path[5:]
    elif normalized_path.startswith("/Root/"):
        normalized_path = normalized_path[6:]

    if not normalized_path:
        return root_comp

    current = root_comp
    for segment in [part for part in normalized_path.split("/") if part]:
        match = None
        for occ in current.occurrences:
            occ_name = getattr(occ, 'name', '')
            comp_name = get_component_name(occ.component)
            if names_match(occ_name, segment) or names_match(comp_name, segment):
                match = occ.component
                break
        if not match:
            return None
        current = match
    return current

def resolve_component_context(component_name=None, component_path=None):
    if component_path:
        return find_component_by_path(root, component_path)
    if component_name:
        if names_match(component_name, "Root"):
            return root
        return find_component_by_name_recursive(root, component_name)
    return active_comp or root

def resolve_lookup_scope(component_name=None, component_path=None):
    target_scope = resolve_component_context(component_name, component_path)
    return target_scope if target_scope else None

def get_component_plane(component, plane_name):
    plane_key = str(plane_name or "XY").upper()
    return {
        "XY": component.xYConstructionPlane,
        "XZ": component.xZConstructionPlane,
        "YZ": component.yZConstructionPlane,
    }.get(plane_key, component.xYConstructionPlane)

def resolve_body_context(target_name, component_name=None, component_path=None):
    scope = resolve_lookup_scope(component_name, component_path)
    body = None
    if scope:
        body = find_body_recursive(scope, target_name)
    
    # Global fallback if not found in specific scope
    if not body and (component_name or component_path):
        body = find_body_recursive(root, target_name)
        
    if not body:
        return (None, None, "ERR_BODY_NOT_FOUND")
        
    owner = get_owner_component(body)
    return (body, owner, None)

def resolve_sketch_context(target_name, component_name=None, component_path=None):
    scope = resolve_lookup_scope(component_name, component_path)
    sketch = None
    if scope:
        sketch = find_sketch_recursive(scope, target_name)
        
    # Global fallback
    if not sketch and (component_name or component_path):
        sketch = find_sketch_recursive(root, target_name)
        
    if not sketch:
        return (None, None, "ERR_SKETCH_NOT_FOUND")
        
    owner = get_owner_component(sketch)
    return (sketch, owner, None)

def resolve_multi_sketch_context(sketch_names, component_name=None, component_path=None):
    resolved = []
    owner_comp = None
    for sketch_name in sketch_names:
        sketch, current_owner, err = resolve_sketch_context(sketch_name, component_name, component_path)
        if err:
            return (None, None, err)
        if owner_comp is None:
            owner_comp = current_owner
        elif current_owner != owner_comp:
            return (None, None, "ERR_ENTITY_OWNER_MISMATCH")
        resolved.append(sketch)
    return (resolved, owner_comp, None)

def resolve_multi_body_context(body_names, component_name=None, component_path=None):
    resolved = []
    owner_comp = None
    for body_name in body_names:
        body, current_owner, err = resolve_body_context(body_name, component_name, component_path)
        if err:
            return (None, None, err)
        if owner_comp is None:
            owner_comp = current_owner
        elif current_owner != owner_comp:
            return (None, None, "ERR_ENTITY_OWNER_MISMATCH")
        resolved.append(body)
    return (resolved, owner_comp, None)

def get_default_target_component(params=None):
    params = params or {}
    target_comp = resolve_component_context(params.get('component_name'), params.get('component_path'))
    return target_comp if target_comp else None

def collect_component_bodies(component):
    bodies = []
    for i in range(component.bRepBodies.count):
        bodies.append(component.bRepBodies.item(i))
    return bodies

def resolve_sketch_creation_context(params):
    component_name = params.get('component_name')
    component_path = params.get('component_path')
    body_name = params.get('body')
    face_idx = params.get('face_index')

    if body_name is not None:
        target_body, owner_comp, err = resolve_body_context(body_name, component_name, component_path)
        if err:
            return (None, None, err)
        if face_idx is None or face_idx < 0 or face_idx >= target_body.faces.count:
            return (None, None, "ERR_FACE_INDEX")
        return (owner_comp, target_body.faces.item(face_idx), None)

    target_comp = resolve_component_context(component_name, component_path)
    if not target_comp:
        return (None, None, "ERR_COMPONENT_NOT_FOUND")
    return (target_comp, get_component_plane(target_comp, params.get('plane')), None)
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
    # Create offset plane in the same component as the base plane
    owner = base_plane.parentComponent if hasattr(base_plane, 'parentComponent') else root
    planes = owner.constructionPlanes
    plane_input = planes.createInput()
    plane_input.setByOffset(base_plane, adsk.core.ValueInput.createByReal(offset))
    return planes.add(plane_input)

def translate_body(body, x=0.0, y=0.0, z=0.0):
    if abs(x) <= 1e-9 and abs(y) <= 1e-9 and abs(z) <= 1e-9:
        return body
    entities = adsk.core.ObjectCollection.create()
    entities.add(body)
    # Use the component that owns the body, not necessarily root
    move_feats = body.parentComponent.features.moveFeatures
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
    if _I18N_DATA is not None and file_path is None:
        return _I18N_DATA
    if file_path is None:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(os.path.dirname(current_dir), "i18n.json")
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            _I18N_DATA = json.load(f)
            return _I18N_DATA
    except Exception as e:
        print(f"Error loading i18n from {file_path}: {e}")
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
