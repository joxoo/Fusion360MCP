import adsk.core, adsk.fusion, adsk.cam, traceback
import threading
import json
import queue
import subprocess
import os
import signal
import shutil
import sys
import io
import contextlib
from datetime import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer

# --- CONFIGURATION ---
EVENT_ID = 'FusionMCP_Bridge_v9'
CMD_ID = 'FusionMCP_UI_Command'
PANEL_ID = 'SolidScriptsAddinsPanel'
TAB_ID = 'ToolsTab'

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

# UI State & Logging
bridge_host = 'localhost'
bridge_port = 8082
mcp_host = '127.0.0.1'
mcp_port = 8081
command_history = []
MAX_LOG_ENTRIES = 20
handlers = []

def add_to_log(msg):
    global command_history
    timestamp = datetime.now().strftime('%H:%M:%S')
    entry = f"[{timestamp}] {msg}"
    command_history.insert(0, entry)
    if len(command_history) > MAX_LOG_ENTRIES:
        command_history.pop()
    app.log(entry)

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
                
                # Sanitize script: convert CRLF to LF and strip trailing whitespace
                script = script.replace('\r\n', '\n').strip()
                
                log_msg = f"Executing: {script[:50]}..." if len(script) > 50 else f"Executing: {script}"
                add_to_log(log_msg)
                
                exec_globals = {
                    'app': app, 'ui': ui, 'adsk': adsk, 
                    'traceback': traceback, 'returnValue': [],
                    'params': params,
                    'start_mcp_server': start_mcp_server,
                    'stop_mcp_process': stop_mcp_process
                }
                
                try:
                    # Redirect stdout to capture print() statements
                    f = io.StringIO()
                    with contextlib.redirect_stdout(f):
                        exec(script, exec_globals)
                    
                    # Add captured stdout to returnValue if it's not empty
                    stdout_content = f.getvalue().strip()
                    if stdout_content:
                        exec_globals['returnValue'].append(stdout_content)
                        
                    last_result = {"status": "success", "data": exec_globals['returnValue'], "error": None}
                    add_to_log("Result: Success")
                except Exception as e:
                    err_msg = str(e)
                    app.log(f"Script Error: {err_msg}")
                    last_result = {"status": "error", "data": None, "error": err_msg}
                    add_to_log(f"Result: Error - {err_msg}")
                
                task_queue.task_done()
            completion_event.set()
        except:
            app.log('Handler Fatal Error: ' + traceback.format_exc())
            completion_event.set()

class BridgeHttpHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args): pass # Mute console noise

    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        status = {"status": "bridge_online", "version": "v9", "queue_size": task_queue.qsize(), "mcp_running": mcp_process is not None}
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
    global http_server, bridge_host, bridge_port
    try:
        http_server = HTTPServer((bridge_host, bridge_port), BridgeHttpHandler)
        http_server.serve_forever()
    except Exception as e:
        app.log(f"Bridge Server Error: {str(e)}")

def restart_bridge():
    global http_server
    try:
        if http_server:
            threading.Thread(target=http_server.shutdown).start()
        threading.Thread(target=run_server, daemon=True).start()
        add_to_log(f"Bridge restarted on {bridge_host}:{bridge_port}")
    except:
        app.log("Failed to restart bridge:\n" + traceback.format_exc())

def find_uv():
    uv_path = shutil.which('uv')
    if uv_path: return uv_path
    home = os.path.expanduser('~')
    common_paths = []
    if os.name == 'nt':
        local_app_data = os.environ.get('LOCALAPPDATA', '')
        common_paths = [os.path.join(local_app_data, 'Programs', 'uv', 'uv.exe'), os.path.join(home, '.cargo', 'bin', 'uv.exe')]
    else:
        common_paths = ['/usr/local/bin/uv', '/opt/homebrew/bin/uv', os.path.join(home, '.cargo', 'bin', 'uv'), os.path.join(home, '.local', 'bin', 'uv')]
    for path in common_paths:
        if os.path.exists(path): return path
    return None

def start_mcp_server():
    global mcp_process, mcp_host, mcp_port
    try:
        addon_dir = os.path.dirname(__file__)
        log_file = os.path.join(addon_dir, 'mcp_error.log')
        if mcp_process: stop_mcp_process()
        server_script = os.path.join(addon_dir, 'fusion_mcp_server.py')
        req_file = os.path.join(addon_dir, 'requirements.txt')
        uv_path = find_uv()
        if not uv_path:
            add_to_log('Error: "uv" not found.')
            return
        cmd = [uv_path, 'run', '--python', '3.11', '--with-requirements', req_file, 'python', '-u', server_script, '--transport', 'sse', '--port', str(mcp_port), '--host', mcp_host]
        clean_env = os.environ.copy()
        clean_env.pop('PYTHONHOME', None)
        clean_env.pop('PYTHONPATH', None)
        clean_env['PYTHONUNBUFFERED'] = '1'
        if os.path.exists(os.path.join(os.path.expanduser('~'), '.cargo', 'bin')):
            clean_env['PATH'] = os.path.join(os.path.expanduser('~'), '.cargo', 'bin') + os.pathsep + clean_env.get('PATH', '')
        log_handle = open(log_file, 'a')
        popen_kwargs = {'stdout': log_handle, 'stderr': subprocess.STDOUT, 'env': clean_env, 'cwd': addon_dir}
        if os.name == 'nt':
            popen_kwargs['creationflags'] = subprocess.CREATE_NEW_PROCESS_GROUP
        else:
            popen_kwargs['preexec_fn'] = os.setsid
        mcp_process = subprocess.Popen(cmd, **popen_kwargs)
        add_to_log(f'MCP Server started on {mcp_host}:{mcp_port}')
    except Exception as e:
        add_to_log(f'Failed to start MCP Server: {str(e)}')

def stop_mcp_process():
    global mcp_process
    if mcp_process:
        try:
            if os.name == 'nt':
                os.kill(mcp_process.pid, signal.CTRL_BREAK_EVENT)
            else:
                os.killpg(os.getpgid(mcp_process.pid), signal.SIGTERM)
        except:
            try: mcp_process.kill()
            except: pass
        mcp_process = None
        add_to_log('MCP Server stopped.')

# --- UI HANDLERS ---
class McpUiInputChangedHandler(adsk.core.InputChangedEventHandler):
    def notify(self, args):
        global mcp_host, mcp_port, bridge_host, bridge_port
        try:
            event_args = adsk.core.InputChangedEventArgs.cast(args)
            inputs = event_args.inputs
            
            b_host_in = inputs.itemById('bridgeHost')
            b_port_in = inputs.itemById('bridgePort')
            m_host_in = inputs.itemById('mcpHost')
            m_port_in = inputs.itemById('mcpPort')
            active_in = inputs.itemById('mcpActive')
            log_box = inputs.itemById('mcpLog')
            
            if b_host_in: bridge_host = b_host_in.value
            if b_port_in: bridge_port = b_port_in.value
            if m_host_in: mcp_host = m_host_in.value
            if m_port_in: mcp_port = m_port_in.value
            
            if event_args.input.id in ['bridgeHost', 'bridgePort']:
                restart_bridge()
            
            if event_args.input.id == 'mcpActive':
                if active_in.value:
                    start_mcp_server()
                else:
                    stop_mcp_process()
            
            # Update status text and log box
            status_input = inputs.itemById('mcpStatus')
            if status_input:
                status_input.text = 'Status: RUNNING' if mcp_process else 'Status: STOPPED'
            if log_box:
                log_box.text = '\n'.join(command_history) if command_history else 'No commands executed yet.'
        except:
            app.log('Input Changed Failed:\n' + traceback.format_exc())

class McpUiCommandCreatedHandler(adsk.core.CommandCreatedEventHandler):
    def notify(self, args):
        try:
            cmd = args.command
            inputs = cmd.commandInputs
            
            # Bridge Settings Group
            bridgeGroup = inputs.addGroupCommandInput('bridgeGroup', 'Bridge Settings (Fusion Interface)')
            bridgeGroup.isExpanded = False
            bridgeGroupChildren = bridgeGroup.children
            bridgeGroupChildren.addStringValueInput('bridgeHost', 'Bridge Host', bridge_host)
            bridgeGroupChildren.addIntegerSliderCommandInput('bridgePort', 'Bridge Port', 1024, 65535, False).valueOne = bridge_port
            
            # MCP Settings Group
            mcpGroup = inputs.addGroupCommandInput('mcpGroup', 'MCP Server Settings')
            mcpGroup.isExpanded = True
            mcpGroupChildren = mcpGroup.children
            mcpGroupChildren.addStringValueInput('mcpHost', 'MCP Host', mcp_host)
            mcpGroupChildren.addIntegerSliderCommandInput('mcpPort', 'MCP Port', 1024, 65535, False).valueOne = mcp_port
            mcpGroupChildren.addBoolValueInput('mcpActive', 'Server Active', True, '', mcp_process is not None)
            
            status_text = 'Status: RUNNING' if mcp_process else 'Status: STOPPED'
            mcpGroupChildren.addTextBoxCommandInput('mcpStatus', '', status_text, 1, True)
            
            # Command Log View
            logGroup = inputs.addGroupCommandInput('logGroup', 'Command History')
            logGroup.isExpanded = True
            log_text = '\n'.join(command_history) if command_history else 'No commands executed yet.'
            log_input = logGroup.children.addTextBoxCommandInput('mcpLog', '', log_text, 10, True)
            log_input.isFullWidth = True
            
            inputs.addBoolValueInput('mcpRefresh', 'Refresh View', False, '', False)
            
            onInputChanged = McpUiInputChangedHandler()
            cmd.inputChanged.add(onInputChanged)
            handlers.append(onInputChanged)
        except:
            ui.messageBox('Command Created Failed:\n' + traceback.format_exc())

def run(context):
    global custom_event, event_handler
    try:
        # 1. Bridge Setup
        custom_event = app.registerCustomEvent(EVENT_ID)
        event_handler = McpCommandHandler()
        custom_event.add(event_handler)
        threading.Thread(target=run_server, daemon=True).start()
        
        # 2. UI Setup
        cmd_def = ui.commandDefinitions.itemById(CMD_ID)
        if not cmd_def:
            cmd_def = ui.commandDefinitions.addButtonDefinition(CMD_ID, 'FusionMCP', 'Manage MCP Server & View Logs', '')
        
        onCommandCreated = McpUiCommandCreatedHandler()
        cmd_def.commandCreated.add(onCommandCreated)
        handlers.append(onCommandCreated)
        
        tools_tab = ui.allToolbarTabs.itemById(TAB_ID)
        if tools_tab:
            panel = tools_tab.toolbarPanels.itemById(PANEL_ID)
            if panel: panel.controls.addCommand(cmd_def)
        
        add_to_log(f'FusionMCP Bridge started on {bridge_host}:{bridge_port}')
        start_mcp_server()
    except:
        ui.messageBox('Failed to start FusionMCP:\n' + traceback.format_exc())

def stop(context):
    global custom_event, http_server
    try:
        if http_server: threading.Thread(target=http_server.shutdown).start()
        stop_mcp_process()
        if custom_event: app.unregisterCustomEvent(EVENT_ID)
        cmd_def = ui.commandDefinitions.itemById(CMD_ID)
        if cmd_def: cmd_def.deleteMe()
        tools_tab = ui.allToolbarTabs.itemById(TAB_ID)
        if tools_tab:
            panel = tools_tab.toolbarPanels.itemById(PANEL_ID)
            if panel:
                ctrl = panel.controls.itemById(CMD_ID)
                if ctrl: ctrl.deleteMe()
        app.log('FusionMCP stopped.')
    except: pass
