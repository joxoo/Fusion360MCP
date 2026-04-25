# FusionMCP (v9.0.3)

FusionMCP is a Model Context Protocol (MCP) server for Autodesk Fusion 360. It enables AI agents to interact directly with the Fusion 360 API to perform complex design, geometry, and mechanical engineering tasks.

## Features

- **Bridge Integration**: A Fusion 360 add-in that bridges external requests to the Fusion 360 main UI thread.
- **MCP Server**: Implements the Model Context Protocol using FastMCP for seamless tool integration.
- **Comprehensive Toolset**:
  - **Design**: General design and project management.
  - **Geometry**: Creation of primitive shapes (box, bolt) and sketches.
  - **Mechanical**: Specialized tools for holes, grooves, and mechanical features.
  - **Export**: Automated STL and F3D export capabilities.
  - **Analysis**: Real-time physical data and body analysis.
  - **Threads**: Support for standard and custom thread application.

## Installation

1. **Prerequisites**: Ensure you have [uv](https://github.com/astral-sh/uv) installed on your system.
2. **Add-In Setup**: Copy this `FusionMCP` folder into your Fusion 360 Add-Ins directory.
   - macOS: `~/Library/Application Support/Autodesk/Autodesk Fusion 360/API/AddIns/`
   - Windows: `%appdata%\Autodesk\Autodesk Fusion 360\API\AddIns\`
3. **Dependencies**: The add-in uses `uv` to manage its own environment, but you can manually install requirements if needed:
   ```bash
   pip install -r requirements.txt
   ```
4. **Activation**: Start the add-in from within Fusion 360 via the **Scripts and Add-Ins** dialog (Shift+S).

## Architecture

The system operates via two primary components:
1. **The Bridge (`FusionMCP.py`)**: Runs as a native Fusion 360 add-in. It hosts a local HTTP server (port 8082) to receive commands and uses `CustomEvent` to execute them safely on the UI thread.
2. **The MCP Server (`fusion_mcp_server.py`)**: A separate process (started automatically by the Bridge via `uv`) that translates MCP tool calls into bridge-compatible requests.

## Project Structure

- `FusionMCP.py`: Add-in entry point and command bridge.
- `fusion_mcp_server.py`: FastMCP server entry point.
- `modules/`: Contains the modular tool implementations:
  - `design.py`, `geometry.py`, `mechanical.py`, etc.
- `FusionMCP.manifest`: Autodesk manifest file.
