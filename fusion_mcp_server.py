import sys
import logging
import argparse
import os

# Ensure logs go to stderr so they don't interfere with stdio communication
logging.basicConfig(level=logging.INFO, stream=sys.stderr)
logger = logging.getLogger("fusion-mcp")

logger.info("Fusion MCP Server script started.")

from mcp.server.fastmcp import FastMCP
from core.utils import register_tool
from modules.design import (
    register_design_tools,
    manage_design_logic,
    describe_tool_actions_logic,
)
from modules.geometry import (
    register_geometry_tools,
    apply_3d_features_logic,
)
from modules.analysis import (
    register_analysis_tools,
    analyze_design_logic,
)
from modules.parameters import (
    register_parameter_tools,
    list_parameters_logic,
    edit_parameters_logic,
)
from modules.assembly import (
    register_assembly_tools,
    edit_assembly_logic,
)
from modules.sketch import (
    register_sketch_tools,
    create_sketch_logic,
    edit_sketch_logic,
)
from modules.surfaces import (
    register_surface_tools,
    edit_surfaces_logic,
)
from modules.mesh import (
    register_mesh_tools,
    import_mesh_logic,
    edit_mesh_logic,
)
from modules.forms import (
    register_form_tools,
    edit_forms_logic,
)
from modules.advanced_geometry import register_advanced_geometry_tools
from modules.export import (
    register_export_tools,
    export_model_logic,
)
from modules.mechanical import register_mechanical_tools
from modules.threads import register_thread_tools


def register_compact_tools(mcp: FastMCP) -> None:
    """Register only the compact public API intended for AI clients."""
    register_tool(mcp, "manage_design", manage_design_logic)
    register_tool(mcp, "describe_tool_actions", describe_tool_actions_logic)
    register_tool(mcp, "analyze_design", analyze_design_logic)
    register_tool(mcp, "list_parameters", list_parameters_logic)
    register_tool(mcp, "edit_parameters", edit_parameters_logic)
    register_tool(mcp, "create_sketch", create_sketch_logic)
    register_tool(mcp, "edit_sketch", edit_sketch_logic)
    register_tool(mcp, "apply_3d_features", apply_3d_features_logic)
    register_tool(mcp, "edit_assembly", edit_assembly_logic)
    register_tool(mcp, "edit_surfaces", edit_surfaces_logic)
    register_tool(mcp, "edit_forms", edit_forms_logic)
    register_tool(mcp, "import_mesh", import_mesh_logic)
    register_tool(mcp, "edit_mesh", edit_mesh_logic)
    register_tool(mcp, "export_model", export_model_logic)
    from modules.geometry import execute_python_script_logic
    register_tool(mcp, "execute_python_script", execute_python_script_logic)


def register_api_profile(mcp: FastMCP, api_profile: str) -> None:
    if api_profile == "full":
        register_design_tools(mcp)
        register_geometry_tools(mcp)
        register_analysis_tools(mcp)
        register_parameter_tools(mcp)
        register_assembly_tools(mcp)
        register_sketch_tools(mcp)
        register_surface_tools(mcp)
        register_mesh_tools(mcp)
        register_form_tools(mcp)
        register_advanced_geometry_tools(mcp)
        register_export_tools(mcp)
        register_mechanical_tools(mcp)
        register_thread_tools(mcp)
    else:
        register_compact_tools(mcp)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fusion MCP Server")
    parser.add_argument("--transport", type=str, default="sse", choices=["stdio", "sse", "streamable-http"])
    parser.add_argument("--port", type=int, default=8081)
    parser.add_argument("--host", type=str, default="127.0.0.1")
    parser.add_argument(
        "--api-profile",
        type=str,
        default=os.environ.get("FUSION_MCP_API_PROFILE", "compact"),
        choices=["compact", "full"],
        help="Expose a compact public API for AI clients or the full internal toolset.",
    )
    
    args, unknown = parser.parse_known_args()
    mcp = FastMCP("Fusion360")
    register_api_profile(mcp, args.api_profile)
    logger.info("Registered API profile: %s", args.api_profile)
    
    if args.transport == "stdio":
        mcp.run(transport="stdio")
    else:
        import uvicorn
        from starlette.applications import Starlette
        from starlette.routing import Mount, Route
        from starlette.responses import JSONResponse

        # Get the underlying SSE/HTTP app
        mcp_app = mcp.sse_app() if args.transport == "sse" else mcp.streamable_http_app()

        async def root_status(request):
            return JSONResponse({
                "status": "mcp_server_online",
                "transport": args.transport,
                "sse_endpoint": "/mcp/sse",
                "messages_endpoint": "/mcp/messages"
            })

        app = Starlette(routes=[
            Route("/mcp", endpoint=root_status),
            Mount("/mcp", app=mcp_app),
            Mount("/", app=mcp_app)
        ])

        logger.info(f"Starting MCP server on {args.host}:{args.port} (transport={args.transport})")
        uvicorn.run(app, host=args.host, port=args.port)
