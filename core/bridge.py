import requests
import json

FUSION_BRIDGE_URL = "http://localhost:8082"

class FusionBridgeError(Exception):
    """Eigene Exception für Fehler in der Fusion-Bridge."""
    pass

def execute_fusion_script(script: str, params: dict = None, timeout: int = 20) -> dict:
    """
    Führt Python-Code in Fusion 360 aus.
    Übergibt Parameter sicher als JSON-Payload, um Code-Injection zu vermeiden.
    """
    payload = {
        "action": "execute_python", 
        "payload": {
            "script": script,
            "params": params or {}
        }
    }
    try:
        response = requests.post(FUSION_BRIDGE_URL, json=payload, timeout=timeout)
        if response.status_code == 200:
            result = response.json()
            if result.get("status") == "error":
                raise FusionBridgeError(result.get("message", "Unbekannter Bridge-Fehler"))
            return result
        else:
            raise FusionBridgeError(f"HTTP Fehler {response.status_code}: {response.text}")
    except requests.exceptions.RequestException as e:
        raise FusionBridgeError(f"Verbindung zur Fusion-Bridge fehlgeschlagen: {str(e)}")

def get_i18n_data(base_path: str):
    try:
        with open(base_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {}
