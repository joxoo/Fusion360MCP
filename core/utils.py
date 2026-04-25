import json

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

def format_response(lang, key_de, key_en, **kwargs):
    """Formats return messages based on the requested language."""
    templates = {
        "de": key_de,
        "en": key_en
    }
    return templates.get(lang, key_en).format(**kwargs)

def get_tool_definition(i18n_data, tool_key):
    """Extracts name and description for a tool from i18n data."""
    de = i18n_data.get("de", {}).get("tools", {}).get(tool_key, {})
    en = i18n_data.get("en", {}).get("tools", {}).get(tool_key, {})
    return de, en
