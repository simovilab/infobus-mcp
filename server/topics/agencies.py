from fastmcp import FastMCP

agencies_mcp = FastMCP("AgenciesServer")


@agencies_mcp.tool(
    name="agencies_info",
    description="Get a list of transit agencies.",
)
async def info() -> list:
    """Get a list of transit agencies."""
    return [
        {"id": "agency_1", "name": "Transit Agency 1"},
        {"id": "agency_2", "name": "Transit Agency 2"},
    ]
