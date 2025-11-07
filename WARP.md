# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Project Overview

Infobús MCP is a Model Context Protocol (MCP) server that enables AI assistants and chatbots to access transit information through standardized interfaces. It provides tools for trip planning, real-time information queries, and natural language transit assistance.

## Repository Structure

This is a monorepo with two main components:

- **`server/`**: Python-based MCP server implementation using FastMCP (primary focus)
- **`client/`**: Client implementation (currently minimal)

All Python code and dependencies are in the `server/` directory.

### Server Directory Structure

```
server/
├── transit.py              # Main entry point - imports and composes subservers
├── topics/                 # Domain-specific subservers (modular architecture)
│   ├── agencies.py         # Agency listing tools
│   ├── routes.py           # Route information tools
│   ├── stops.py            # Stop info and next trips (fully implemented)
│   ├── trips.py            # Trip planning (planned)
│   ├── alerts.py           # Service alerts (planned)
│   └── shapes.py           # Route shapes (planned)
└── utils/
    └── infobus_requests.py # Shared API request utilities
```

## Development Environment

### Prerequisites

- Python 3.14 (specified in `server/.python-version`)
- `uv` package manager for Python dependency management

### Initial Setup

```bash
cd server
uv venv
source .venv/bin/activate  # On macOS/Linux
uv sync  # Install dependencies from uv.lock
```

### Running the MCP Server

The server runs using stdio transport for MCP communication:

```bash
# From project root
uv --directory server run transit.py

# Or from server directory
cd server
python transit.py
```

The server must be run with stdio transport as it's designed to be called by MCP clients (Claude Desktop, etc.), not standalone.

### VS Code MCP Configuration

The project includes VS Code MCP configuration in `.vscode/mcp.json` that runs the server using:
```bash
uv --directory server run transit.py
```

### Testing

**No automated tests are currently implemented.** To test changes:

1. Run the server using one of the methods above
2. Connect via an MCP client (Claude Desktop, VS Code MCP extension)
3. Test tools manually through the client interface
4. Verify API responses using the Infobús API directly: `https://infobus.bucr.digital/api`

## Architecture

### MCP Server Implementation

The project uses the **FastMCP** framework with a **modular subserver architecture**.

**Architecture Overview:**
- `server/transit.py`: Main server entry point that imports and composes domain-specific subservers
- `server/topics/`: Directory containing modular subservers, each focused on a specific domain (agencies, routes, stops, trips, etc.)
- Each subserver is imported with a prefix (e.g., `agencies`, `routes`, `stops`) in `transit.py` using `mcp.import_server()`
- Subservers are independent FastMCP instances that can be developed and tested in isolation

**Key Pattern:**
```python
# In transit.py
async def setup():
    await mcp.import_server(agencies_mcp, prefix="agencies")
    await mcp.import_server(routes_mcp, prefix="routes")
    await mcp.import_server(stops_mcp, prefix="stops")
```

This allows tools from each subserver to be namespaced (e.g., `agencies_info`, `routes_info`, `stops_next_trips`).

### MCP Tools

Tools are exposed via the `@<subserver>.tool()` decorator in their respective topic modules. 

**Fully Implemented:**
- **`stops_next_trips(stop_id: str, timestamp: str)`**: Fetches next arriving buses at a given stop
  - Returns up to 4 next arrivals
  - Timestamp format: ISO 8601 (YYYY-MM-DDTHH:MM:SS)
  - Uses GTFS stop IDs
  - Implemented in `server/topics/stops.py`

- **`stops_info(stop_id: str)`**: Get information about a specific bus stop (placeholder)
- **`routes_info(route_id: str)`**: Get information about a route (placeholder)
- **`agencies_info()`**: Get list of transit agencies (placeholder)

**Partially Implemented/Planned:**
- Trips, alerts, calendar, fares, shapes modules exist but are empty/placeholders

### Infobús API Integration

The server integrates with the Infobús API at `https://infobus.bucr.digital/api`

**API Communication:**
- Uses `httpx` for async HTTP requests
- `make_infobus_request()` in `server/utils/infobus_requests.py` handles all API calls with error handling
- Returns error dictionaries on failure rather than raising exceptions
- User-Agent configured via `USER_AGENT` environment variable (defaults to "transit-app/1.0")
- 30-second timeout on requests
- Follows redirects automatically

**API Endpoints Used:**
- `/next-trips/`: Get next trips for a stop at a given time

### Error Handling Pattern

The codebase uses a consistent error handling pattern:
1. API requests return `{"error": "..."}` on failure
2. Tools check for "error" key in responses
3. Tools return user-friendly error messages as strings
4. Format functions (like `format_next_arrival`) handle missing data gracefully

## Adding New MCP Tools

When adding new tools, decide whether to add to an existing topic subserver or create a new one.

**To add to existing subserver:**
1. Open the appropriate file in `server/topics/` (e.g., `stops.py`, `routes.py`)
2. Use the `@<subserver>.tool()` decorator (e.g., `@stops_mcp.tool()`)
3. Provide clear docstrings with Args documentation
4. Use `make_infobus_request()` from `utils.infobus_requests` for API calls
5. Return formatted strings, not raw JSON
6. Handle error cases explicitly by checking for "error" key
7. Limit data returned to users (e.g., first 4 arrivals)

**To create a new subserver:**
1. Create new file in `server/topics/` (e.g., `calendar.py`)
2. Initialize a new FastMCP instance: `calendar_mcp = FastMCP(name="CalendarServer")`
3. Add tools using `@calendar_mcp.tool()` decorator
4. Import and register in `server/transit.py`:
   ```python
   from topics.calendar import calendar_mcp
   
   async def setup():
       # ...
       await mcp.import_server(calendar_mcp, prefix="calendar")
   ```

Example tool structure:
```python
from fastmcp import FastMCP
from utils.infobus_requests import make_infobus_request
from decouple import config

stops_mcp = FastMCP(name="StopsServer")
INFOBUS_API_BASE = config("INFOBUS_API_BASE", default="http://localhost:8000/api")

@stops_mcp.tool()
async def your_tool_name(param: str) -> str:
    """Tool description.
    
    Args:
        param: Parameter description
    """
    url = f"{INFOBUS_API_BASE}/endpoint/"
    params = {"param": param}
    data = await make_infobus_request(url, params)
    
    if "error" in data:
        return f"Error: {data['error']}"
    
    # Format and return data
    return formatted_result
```

## Dependencies

Core dependencies (from `pyproject.toml`):
- `fastmcp>=2.12.5`: FastMCP framework for building MCP servers
- `httpx>=0.28.1`: Async HTTP client for API requests
- `python-decouple>=3.8`: Configuration management via environment variables

## Configuration

Configuration is handled via `python-decouple` which reads from environment variables or `.env` files:

- **`INFOBUS_API_BASE`**: Base URL for Infobús API (default: `http://localhost:8000/api`)
  - Each topic module that needs API access should define this constant
  - Production value should be `https://infobus.bucr.digital/api`
- **`USER_AGENT`**: User agent string for API requests (default: `transit-app/1.0`)
  - Defined in `server/utils/infobus_requests.py`
- Python version pinned to 3.14 in `server/.python-version`
