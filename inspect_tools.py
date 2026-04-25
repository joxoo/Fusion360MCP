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
    tools = response.json()
    for tool in tools.get('result', {}).get('tools', []):
        if tool['name'] == 'create_box':
            print(json.dumps(tool, indent=2))
except Exception as e:
    print(f"Error: {e}")
