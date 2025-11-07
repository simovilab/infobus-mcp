from fastmcp import FastMCP
import asyncio

from topics.agencies import agencies_mcp
from topics.routes import routes_mcp
from topics.stops import stops_mcp

# Initialize FastMCP server
mcp = FastMCP("transit")


# Import subservers
async def setup():
    await mcp.import_server(agencies_mcp, prefix="agencies")
    await mcp.import_server(routes_mcp, prefix="routes")
    await mcp.import_server(stops_mcp, prefix="stops")


if __name__ == "__main__":
    # Initialize and run the server
    asyncio.run(setup())
    mcp.run(transport="stdio")
