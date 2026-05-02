# FusionMCP (v9.4.0)

FusionMCP is a Model Context Protocol (MCP) server for Autodesk Fusion 360. It enables AI agents to interact directly with the Fusion 360 API to perform complex design, geometry, and mechanical engineering tasks.

## Features

- **Bridge Integration**: A Fusion 360 add-in that bridges external requests to the Fusion 360 main UI thread.
- **MCP Server**: Implements the Model Context Protocol using FastMCP for seamless tool integration.
- **Compact Public API**: By default, the server exposes a reduced AI-friendly toolset. The full internal toolset can still be enabled explicitly.
- **Comprehensive Toolset**:
  - **Compact profile**: `manage_design`, `describe_tool_actions`, `analyze_design`, `list_parameters`, `edit_parameters`, `create_sketch`, `edit_sketch`, `apply_3d_features`, `edit_assembly`, `edit_surfaces`, `edit_forms`, `import_mesh`, `edit_mesh`, `export_model`.
  - **Full profile**: Adds advanced/internal tools such as direct API access, appearance, measurement, threads, mechanical helpers, and other specialist endpoints.

## Recent Changes

- `edit_sketch` now exposes a much broader compact sketch API: text, richer rectangle/polygon/slot variants, SVG import, spun profiles, projection/include helpers, sketch redefine, and connected-curve discovery.
- `apply_3d_features` now exposes a much broader compact solid-modeling API: `create_hole`, `draft`, loft/sweep/revolve, solid patterns, feature patterns, construction helpers, thread/coil helpers, body correction actions, and more corrective feature operations.
- `edit_assembly` now includes `rename_component`, `delete_component`, `move_component`, `create_as_built_joint`, and `set_contact_sets`.
- `analyze_design` now includes `get_feature_history`, `interference_check`, `capture_view`, and `capture_side`.
- `execute_python_script` is now part of the public compact API for expert-level direct Fusion Python workflows.
- Compact tool guidance was expanded substantially so AI clients can use the public API with clearer action-specific parameter contracts.
- Sketch batch execution now handles slot creation, projection paths, dimensions, constraints, and error reporting more robustly against current Fusion API behavior.

## Installation

1. **Prerequisites**: Ensure you have [uv](https://github.com/astral-sh/uv) installed on your system.
2. **Add-In Setup**: Copy this `FusionMCP` folder into your Fusion 360 Add-Ins directory.
   - macOS: `~/Library/Application Support/Autodesk/Autodesk Fusion 360/API/AddIns/`
   - Windows: `%appdata%\Autodesk\Autodesk Fusion 360\API\AddIns\`
   - Windows installer for end users: build and distribute `installer/windows/FusionMCP.iss` as a normal Setup EXE
   - Windows script-based install for developers: run `scripts\install_windows.cmd` or `powershell -ExecutionPolicy Bypass -File .\scripts\install_windows.ps1`
   - CI build: `.github/workflows/build-windows-installer.yml` creates the Windows Setup EXE on GitHub Actions and uploads it as an artifact
   - Release build: `.github/workflows/release-windows-installer.yml` builds the same installer for Git tags / GitHub releases and attaches it to the release
3. **Dependencies**: The add-in uses `uv` to manage its own environment, but you can manually install requirements if needed:
   ```bash
   pip install -r requirements.txt
   ```
4. **Activation**: Start the add-in from within Fusion 360 via the **Scripts and Add-Ins** dialog (Shift+S).

## Architecture

The system operates via two primary components:
1. **The Bridge (`FusionMCP.py`)**: Runs as a native Fusion 360 add-in. It hosts a local HTTP server (port 8082) to receive commands and uses `CustomEvent` to execute them safely on the UI thread.
2. **The MCP Server (`fusion_mcp_server.py`)**: A separate process (started automatically by the Bridge via `uv`) that translates MCP tool calls into bridge-compatible requests.

### API Profiles

- `compact` (default): exposes the reduced public API intended for AI clients.
- `full`: exposes the larger internal/specialist toolset.

You can switch profiles with:

```bash
python fusion_mcp_server.py --api-profile full
```

or via:

```bash
FUSION_MCP_API_PROFILE=full
```

## Project Structure

- `FusionMCP.py`: Add-in entry point and command bridge.
- `fusion_mcp_server.py`: FastMCP server entry point.
- `modules/`: Contains the modular tool implementations:
  - `design.py`, `geometry.py`, `mechanical.py`, etc.
- `modules/tool_action_guides.json`: Extracted action guidance used by `describe_tool_actions`.
- `docs/AI_USAGE.md`: Generated compact public API usage rules for AI clients.
- `scripts/generate_ai_usage.py`: Regenerates `docs/AI_USAGE.md` from `modules/tool_action_guides.json`.
- `FusionMCP.manifest`: Autodesk manifest file.
