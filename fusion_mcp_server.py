import sys
import logging

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
    mcp.run()
