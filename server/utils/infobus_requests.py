from decouple import config
from typing import Any
import httpx


USER_AGENT = config("USER_AGENT", default="transit-app/1.0")


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
