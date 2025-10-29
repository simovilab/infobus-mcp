from typing import Any
import httpx
from fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("transit")

# Constants
INFOBUS_API_BASE = "https://infobus.bucr.digital/api"
USER_AGENT = "transit-app/1.0"


async def make_infobus_request(url: str, params: dict) -> dict[str, Any]:
    """Make a request to the Infobús(R) API with proper error handling."""
    headers = {"User-Agent": USER_AGENT, "Accept": "application/json"}
    async with httpx.AsyncClient(follow_redirects=True) as client:
        try:
            response = await client.get(
                url, headers=headers, params=params, timeout=30.0
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            # Return a dictionary with an error key instead of None
            return {"error": f"{type(e).__name__}: {str(e)}"}


def format_next_arrival(arrival: dict) -> str:
    """Format an arriving trip into a readable string."""
    if not arrival:
        return "No arrival data available."
    return f"""
Route short name: {arrival.get("route_short_name", "Unknown")}
Route long name: {arrival.get("route_long_name", "Unknown")}
Going to (headsign): {arrival.get("trip_headsign", "Unknown")}
Arrival time: {arrival.get("arrival_time", "Unknown")}
"""


@mcp.tool()
async def get_next_trips(stop_id: str, timestamp: str) -> str:
    """Get next trips for a given bus stop in a given day and time.

    Args:
        stop_id: GTFS stop ID
        timestamp: Timestamp in ISO 8601 format (YYYY-MM-DDTHH:MM:SS)
    """
    url = f"{INFOBUS_API_BASE}/next-trips/"
    params = {
        "stop_id": stop_id,
        "timestamp": timestamp,
    }
    data = await make_infobus_request(url, params)

    # Check if there was an error during the request
    if "error" in data:
        return f"The API call did not work. Error: {data['error']}"

    # Check if next_arrivals key exists
    if "next_arrivals" not in data:
        return f"Unexpected API response format. Received: {str(data)[:200]}"

    # Check if there are any arrivals
    if not data["next_arrivals"]:
        return "No arrivals for this bus stop at this time."

    # Limit to first 4 arrivals and format them
    arrivals = data["next_arrivals"][:4]
    formatted_arrivals = [format_next_arrival(arrival) for arrival in arrivals]
    return "\n---\n".join(formatted_arrivals)


if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport="stdio")
