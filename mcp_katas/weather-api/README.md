# Weather API MCP Server

## Goal

Build an MCP server that provides weather information using the wttr.in API (free, no API key required).

## Challenge

Your MCP server should expose tools to:
- Get current weather for a location
- Get weather forecast
- Support different units (metric/imperial)

## API Information

**wttr.in** is a free weather service:
- URL: `https://wttr.in/{location}?format=j1`
- No API key required
- Returns JSON with comprehensive weather data
- Supports city names, coordinates, airport codes

Example request:
```bash
curl "https://wttr.in/London?format=j1"
```

## MCP Server Structure

Your server should expose these tools:

### get_weather
- **location** (string): City name or location
- **units** (string, optional): "metric" or "imperial" (default: metric)

Returns current weather conditions including:
- Temperature
- Conditions (sunny, cloudy, rainy, etc.)
- Humidity
- Wind speed

### get_forecast
- **location** (string): City name or location
- **days** (int, optional): Number of days (1-3, default: 3)
- **units** (string, optional): "metric" or "imperial"

Returns weather forecast for upcoming days.

## Getting Started

```bash
# Install dependencies
uv sync

# Implement the tools in server.py using fastmcp

# Run the MCP server
uv run server.py

# Test with MCP inspector
npx @modelcontextprotocol/inspector uv run server.py
```

## Implementation Hints

Use fastmcp's `@mcp.tool()` decorator:

```python
from fastmcp import FastMCP
import httpx

mcp = FastMCP("weather-api")

@mcp.tool()
async def get_weather(location: str, units: str = "metric") -> str:
    # Your implementation here
    pass
```

## Testing

Test your server using the MCP inspector or by connecting it to Claude Desktop.

## Resources

- [MCP Documentation](https://modelcontextprotocol.io/)
- [wttr.in GitHub](https://github.com/chubin/wttr.in)
