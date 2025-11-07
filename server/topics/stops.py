from fastmcp import FastMCP
from utils.infobus_requests import make_infobus_request
from decouple import config

stops_mcp = FastMCP(name="StopsServer")


INFOBUS_API_BASE = config("INFOBUS_API_BASE", default="http://localhost:8000/api")


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


@stops_mcp.tool()
async def info(stop_id: str) -> str:
    """Get information about a specific bus stop.

    Args:
        stop_id: GTFS stop ID
    """
    # Placeholder implementation
    return f"Information for stop ID {stop_id} is: it is wheelchair accessible."


@stops_mcp.tool()
async def next_trips(stop_id: str, timestamp: str) -> str:
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


"""
Other possible tools:

- Weather at stop
- Nearby amenities
- Stop schedule (next arrivals)
"""
