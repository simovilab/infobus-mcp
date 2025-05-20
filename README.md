# Interfaz de inteligencia artificial en sistemas de información para personas usuarias del transporte público

Fabián Abarca Calderón

Nota: manejador de paquetes de Python uv.

```bash
uv init transit
cd transit
```

```bash
uv venv
source .venv/bin/activate
```

```bash
uv add "mcp[cli]" httpx
```

```bash
touch transit.py
```

```Python

@mcp.tool()
async def get_forecast(latitude: float, longitude: float) -> str:
    """Get weather forecast for a location.

    Args:
        latitude: Latitude of the location
        longitude: Longitude of the location
    """
    # First get the forecast grid endpoint
    points_url = f"{INFOBUS_API_BASE}/points/{latitude},{longitude}"
    points_data = await make_infobus_request(points_url)

    if not points_data:
        return "Unable to fetch forecast data for this location."

    # Get the forecast URL from the points response
    forecast_url = points_data["properties"]["forecast"]
    forecast_data = await make_infobus_request(forecast_url)

    if not forecast_data:
        return "Unable to fetch detailed forecast."

    # Format the periods into a readable forecast
    periods = forecast_data["properties"]["periods"]
    forecasts = []
    for period in periods[:5]:  # Only show next 5 periods
        forecast = f"""
{period['name']}:
Temperature: {period['temperature']}°{period['temperatureUnit']}
Wind: {period['windSpeed']} {period['windDirection']}
Forecast: {period['detailedForecast']}
"""
        forecasts.append(forecast)

    return "\n---\n".join(forecasts)
```
