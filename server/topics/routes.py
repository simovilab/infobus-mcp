from fastmcp import FastMCP

routes_mcp = FastMCP(name="RoutesServer")


@routes_mcp.tool(
    name="routes_info",
    description="Get information about a specific bus route.",
    tags={"routes", "gtfs"},
    meta={"version": "0.1"},
)
async def info(route_id: str) -> str:
    """
    Args:
        route_id: GTFS route ID
    """
    # Placeholder implementation
    return f"Information for route ID {route_id} is: it serves multiple stops."
