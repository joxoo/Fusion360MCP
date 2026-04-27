import json
import requests
import sys

# FusionMCP Server URL
url = "http://localhost:8081/mcp/messages"

# MCP listTools request
payload = {
    "jsonrpc": "2.0",
    "id": 1,
    "method": "listTools",
    "params": {}
}

try:
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        data = response.json()
        if "result" in data:
            tools = data["result"].get("tools", [])
            print(f"Found {len(tools)} tools on FusionMCP server:\n")
            for tool in sorted(tools, key=lambda x: x['name']):
                print(f"- {tool['name']}: {tool.get('description', 'No description')}")
        else:
            print("Error: No result in response.")
            print(json.dumps(data, indent=2))
    else:
        print(f"Error: Server returned status code {response.status_code}")
        print(response.text)
except Exception as e:
    print(f"Connection Error: {e}")
