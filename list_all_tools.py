import json
import requests

url = "http://localhost:8081/mcp"
payload = {
    "jsonrpc": "2.0",
    "id": 1,
    "method": "listTools",
    "params": {}
}

try:
    response = requests.post(url, json=payload)
    print(json.dumps(response.json(), indent=2))
except Exception as e:
    print(f"Error: {e}")
