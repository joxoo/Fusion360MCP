from mcp.server.fastmcp import FastMCP
from modules.design import register_design_tools
from modules.geometry import register_geometry_tools
from modules.mechanical import register_mechanical_tools
from modules.export import register_export_tools
from modules.analysis import register_analysis_tools
from modules.threads import register_thread_tools

# Initialisiere den MCP Server
mcp = FastMCP("Fusion360")

# Konfiguration via Settings (wie im Log entdeckt)
mcp.settings.host = "localhost"
mcp.settings.port = 8081
mcp.settings.sse_path = "/mcp"

# Registriere Tools aus den Modulen
register_design_tools(mcp)
register_geometry_tools(mcp)
register_mechanical_tools(mcp)
register_export_tools(mcp)
register_analysis_tools(mcp)
register_thread_tools(mcp)

if __name__ == "__main__":
    # In dieser Version nimmt run() keine Port/Host Argumente an
    mcp.run(transport='sse')
