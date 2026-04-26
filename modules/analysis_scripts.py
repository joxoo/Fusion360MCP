def build_capture_view_script() -> str:
    return """import base64, os, tempfile
try:
    view = app.activeViewport
    temp_dir = tempfile.gettempdir()
    file_path = os.path.join(temp_dir, 'fusion_screenshot.png')
    view.saveAsImageFile(file_path, 0, 0)
    with open(file_path, 'rb') as f:
        encoded = base64.b64encode(f.read()).decode('utf-8')
    os.remove(file_path)
    returnValue.append(encoded)
except Exception as e:
    returnValue.append(f"Error: {str(e)}")"""


def build_analyze_bodies_script() -> str:
    return """import json
try:
    bodies_info = []
    for b in root.bRepBodies:
        bodies_info.append({
            "name": b.name,
            "volume": b.volume,
            "area": b.area,
            "visible": b.isVisible
        })
    returnValue.append(json.dumps(bodies_info))
except Exception as e:
    returnValue.append(f"Error: {str(e)}")"""
