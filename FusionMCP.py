import adsk.core, adsk.fusion, adsk.cam, traceback
import threading
import json
import queue
import subprocess
import os
import signal
import shutil
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer

# --- CONFIGURATION ---
PORT = 8082
EVENT_ID = 'FusionMCP_Bridge_v9'

# --- GLOBALS ---
app = adsk.core.Application.get()
ui = app.userInterface
task_queue = queue.Queue()
completion_event = threading.Event()
last_result = {"status": "idle", "data": None, "error": None}
custom_event = None
event_handler = None
http_server = None
mcp_process = None

class BridgeResponse:
    @staticmethod
    def success(data=None, detail=None):
        return {"version": "v9", "status": "success", "data": data, "detail": detail}
    
    @staticmethod
    def error(message):
        return {"version": "v9", "status": "error", "message": message}

class McpCommandHandler(adsk.core.CustomEventHandler):
    def notify(self, args):
        global last_result
        try:
            while not task_queue.empty():
                task = task_queue.get()
                payload = task.get('payload', {})
                script = payload.get('script', '')
                params = payload.get('params', {})
                
                exec_globals = {
                    'app': app, 'ui': ui, 'adsk': adsk, 
                    'traceback': traceback, 'returnValue': [],
                    'params': params
                }
                
                try:
                    exec(script, exec_globals)
                    last_result = {"status": "success", "data": exec_globals['returnValue'], "error": None}
                except Exception as e:
                    app.log(f"Script Error: {str(e)}")
                    last_result = {"status": "error", "data": None, "error": str(e)}
                
                task_queue.task_done()
            completion_event.set()
        except:
            app.log('Handler Fatal Error: ' + traceback.format_exc())
            completion_event.set()

class McpHttpHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args): pass # Mute console noise

    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        status = {"status": "online", "version": "v9", "queue_size": task_queue.qsize()}
        self.wfile.write(json.dumps(status).encode('utf-8'))

    def do_POST(self):
        global last_result
        try:
            content_length = int(self.headers['Content-Length'])
            data = json.loads(self.rfile.read(content_length).decode('utf-8'))
            
            completion_event.clear()
            task_queue.put(data)
            app.fireCustomEvent(EVENT_ID, "run")

            if not completion_event.wait(timeout=15.0):
                res = BridgeResponse.error("Timeout: Fusion 360 UI thread not responding")
            else:
                if last_result["status"] == "success":
                    res = BridgeResponse.success(last_result["data"])
                else:
                    res = BridgeResponse.error(last_result["error"])

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(res).encode('utf-8'))
        except Exception as e:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(json.dumps(BridgeResponse.error(str(e))).encode('utf-8'))

def run_server():
    global http_server
    try:
        http_server = HTTPServer(('localhost', PORT), McpHttpHandler)
        http_server.serve_forever()
    except: pass

def find_uv():
    """Sucht aggressiv nach uv in PATH und g\u00e4ngigen Installationspfaden."""
    # 1. Standard PATH Suche
    uv_path = shutil.which('uv')
    if uv_path: return uv_path
    
    # 2. Bekannte Pfade
    home = os.path.expanduser('~')
    common_paths = []
    if os.name == 'nt': # Windows
        local_app_data = os.environ.get('LOCALAPPDATA', '')
        common_paths = [
            os.path.join(local_app_data, 'Programs', 'uv', 'uv.exe'),
            os.path.join(home, '.cargo', 'bin', 'uv.exe')
        ]
    else: # macOS / Linux
        common_paths = [
            '/usr/local/bin/uv',
            '/opt/homebrew/bin/uv',
            os.path.join(home, '.cargo', 'bin', 'uv'),
            os.path.join(home, '.local', 'bin', 'uv')
        ]
        
    for path in common_paths:
        if os.path.exists(path):
            return path
    return None

def start_mcp_server():
    global mcp_process
    try:
        if mcp_process: stop_mcp_process()

        addon_dir = os.path.dirname(__file__)
        server_script = os.path.join(addon_dir, 'fusion_mcp_server.py')
        req_file = os.path.join(addon_dir, 'requirements.txt')
        log_file = os.path.join(addon_dir, 'mcp_error.log')
        
        uv_path = find_uv()
        if not uv_path:
            app.log('Error: "uv" not found. MCP Server will not start.')
            return

        # Befehl f\u00fcr uv
        cmd = [uv_path, 'run', '--python', '3.11', '--with-requirements', req_file, 'python', server_script]
        app.log(f'MCP Server: Starting via uv at {uv_path}')

        # Log-Datei f\u00fcr Fehler initialisieren
        with open(log_file, 'w') as f:
            f.write(f"Starting MCP Server...\nCmd: {str(cmd)}\n\n")

        # UMGEBUNGSVARIABLEN BEREINIGEN:
        # Fusion 360 setzt PYTHONHOME und PYTHONPATH, was uv/python verwirrt (ModuleNotFoundError: encodings)
        clean_env = os.environ.copy()
        clean_env.pop('PYTHONHOME', None)
        clean_env.pop('PYTHONPATH', None)
        # Optional: PATH erweitern, falls uv weitere Tools braucht
        if os.path.exists(os.path.join(os.path.expanduser('~'), '.cargo', 'bin')):
            clean_env['PATH'] = os.path.join(os.path.expanduser('~'), '.cargo', 'bin') + os.pathsep + clean_env.get('PATH', '')

        # Prozess-Konfiguration
        popen_kwargs = {
            'stdout': open(log_file, 'a'),
            'stderr': subprocess.STDOUT,
            'env': clean_env,
            'cwd': addon_dir # Wichtig f\u00fcr relative Pfade im Skript
        }
        
        if os.name == 'nt':
            popen_kwargs['creationflags'] = subprocess.CREATE_NEW_PROCESS_GROUP
        else:
            popen_kwargs['preexec_fn'] = os.setsid

        mcp_process = subprocess.Popen(cmd, **popen_kwargs)
        app.log('MCP Server subprocess triggered with clean environment.')
    except Exception as e:
        app.log(f'Failed to start MCP Server: {str(e)}')

def stop_mcp_process():
    global mcp_process
    if mcp_process:
        try:
            if os.name == 'nt':
                os.kill(mcp_process.pid, signal.CTRL_BREAK_EVENT)
            else:
                os.killpg(os.getpgid(mcp_process.pid), signal.SIGTERM)
            app.log('MCP Server subprocess stopped.')
        except:
            try: mcp_process.kill()
            except: pass
        mcp_process = None

def run(context):
    global custom_event, event_handler
    try:
        custom_event = app.registerCustomEvent(EVENT_ID)
        event_handler = McpCommandHandler()
        custom_event.add(event_handler)
        
        threading.Thread(target=run_server, daemon=True).start()
        app.log(f'FusionMCP Bridge started on port {PORT}')
        
        start_mcp_server()
    except:
        ui.messageBox('Failed to start FusionMCP:\n' + traceback.format_exc())

def stop(context):
    global custom_event, http_server
    try:
        if http_server: threading.Thread(target=http_server.shutdown).start()
        stop_mcp_process()
        if custom_event: app.unregisterCustomEvent(EVENT_ID)
        app.log('FusionMCP stopped.')
    except: pass
