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
        # fastmcp uses sse_app() to create a Starlette app with /sse and /messages routes
        mcp_app = mcp.sse_app() if args.transport == "sse" else mcp.streamable_http_app()

        # Create a wrapper app to map /mcp to the root of the MCP app
        # This allows accessing the server at http://localhost:8081/mcp/sse etc.
        # To make http://localhost:8081/mcp work directly, we add a redirect or status
        async def root_status(request):
            return JSONResponse({
                "status": "mcp_server_online",
                "transport": args.transport,
                "sse_endpoint": "/mcp/sse",
                "messages_endpoint": "/mcp/messages"
            })

        app = Starlette(routes=[
            Route("/mcp", endpoint=root_status),
            Mount("/mcp", app=mcp_app), # This mounts /sse and /messages under /mcp
            Mount("/", app=mcp_app)      # Also keep original routes for compatibility
        ])

        logger.info(f"Starting MCP server on {args.host}:{args.port} (transport={args.transport})")
        uvicorn.run(app, host=args.host, port=args.port)
