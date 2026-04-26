import sys
import logging
import argparse
import os

# Ensure logs go to stderr so they don't interfere with stdio communication
logging.basicConfig(level=logging.INFO, stream=sys.stderr)
logger = logging.getLogger("fusion-mcp")

logger.info("Fusion MCP Server script started.")

from mcp.server.fastmcp import FastMCP
from modules.design import register_design_tools
from modules.geometry import register_geometry_tools
from modules.mechanical import register_mechanical_tools
from modules.export import register_export_tools
from modules.threads import register_thread_tools
from modules.analysis import register_analysis_tools
from modules.parameters import register_parameter_tools
from modules.assembly import register_assembly_tools
from modules.sketch import register_sketch_tools
from modules.advanced_geometry import register_advanced_geometry_tools

# Create the MCP server instance
mcp = FastMCP("Fusion360")

# Register tools from all modules
register_design_tools(mcp)
register_geometry_tools(mcp)
register_mechanical_tools(mcp)
register_export_tools(mcp)
register_thread_tools(mcp)
register_analysis_tools(mcp)
register_parameter_tools(mcp)
register_assembly_tools(mcp)
register_sketch_tools(mcp)
register_advanced_geometry_tools(mcp)

from modules.design import create_new_design_logic
@mcp.tool(name="test_new_design")
def test_new_design():
    """Manual registration test."""
    return create_new_design_logic(lang="en")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fusion MCP Server")
    parser.add_argument("--transport", type=str, default="sse", choices=["stdio", "sse", "streamable-http"])
    parser.add_argument("--port", type=int, default=8081)
    parser.add_argument("--host", type=str, default="127.0.0.1")
    
    args, unknown = parser.parse_known_args()
    
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
