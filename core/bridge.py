import requests
import json
from .utils import COMMON_FUSION_SCRIPTS

FUSION_BRIDGE_URL = "http://localhost:8082"

class FusionBridgeError(Exception):
    """Custom exception for errors in the Fusion bridge."""
    pass

def execute_fusion_script(script: str, params: dict = None, use_common: list = None, timeout: int = 30) -> dict:
    """
    Executes Python code in Fusion 360.
    Optionally prepends common utility script fragments.
    Always includes standard setup and core resolvers by default.
    """
    # Base fragments that should be available everywhere
    base_keys = ["setup_standard", "find_body", "find_comp", "placement"]
    
    # Track which keys we already added to avoid duplicates
    added_keys = set()
    full_script = ""

    for key in base_keys:
        if key in COMMON_FUSION_SCRIPTS:
            full_script += COMMON_FUSION_SCRIPTS[key]
            added_keys.add(key)
    
    if use_common:
        for key in use_common:
            if key in COMMON_FUSION_SCRIPTS and key not in added_keys:
                full_script += COMMON_FUSION_SCRIPTS[key]
                added_keys.add(key)
    
    full_script += "\n" + script

    payload = {
        "action": "execute_python", 
        "payload": {
            "script": full_script,
            "params": params or {}
        }
    }
    
    try:
        response = requests.post(FUSION_BRIDGE_URL, json=payload, timeout=timeout)
        if response.status_code == 200:
            result = response.json()
            if result.get("status") == "error":
                raise FusionBridgeError(result.get("message", "Unknown bridge error"))
            return result
        else:
            raise FusionBridgeError(f"HTTP Error {response.status_code}: {response.text}")
    except requests.exceptions.RequestException as e:
        raise FusionBridgeError(f"Connection to Fusion bridge failed: {str(e)}")

def get_i18n_data(base_path: str):
    """Loads internationalization data from a JSON file."""
    try:
        with open(base_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return {}
