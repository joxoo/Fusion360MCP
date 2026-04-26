def build_cleanup_design_script() -> str:
    return """try:
    for i in range(root.occurrences.count - 1, -1, -1):
        root.occurrences.item(i).deleteMe()
    for i in range(root.bRepBodies.count - 1, -1, -1):
        root.bRepBodies.item(i).deleteMe()
    returnValue.append("OK")
except Exception as e:
    returnValue.append(f"ERR_API:{str(e)}")"""


def build_restart_mcp_script() -> str:
    return "start_mcp_server(); returnValue.append('OK')"


def build_create_new_design_script() -> str:
    return "app.documents.add(0); returnValue.append('OK')"
