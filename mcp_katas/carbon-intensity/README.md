# Carbon Intensity MCP Server

## Goal

Build an MCP server that provides real-time carbon intensity data for electricity generation using the UK Carbon Intensity API.

## Challenge

Your MCP server should expose tools to:
- Get current carbon intensity for a region or postcode
- Get carbon intensity forecast
- Get generation mix (renewable vs fossil fuel breakdown)

## API Information

**Carbon Intensity API** (UK):
- Base URL: `https://api.carbonintensity.org.uk`
- No API key required
- Free and open data
- Returns carbon intensity in gCO2/kWh

Example requests:
```bash
# Current national intensity
curl "https://api.carbonintensity.org.uk/intensity"

# Regional data
curl "https://api.carbonintensity.org.uk/regional"

# Postcode lookup
curl "https://api.carbonintensity.org.uk/regional/postcode/SW1"
```

## MCP Server Structure

Your server should expose these tools:

### get_current_intensity
- **region** (string, optional): UK region code or postcode
- Returns current carbon intensity and generation mix

### get_intensity_forecast
- **region** (string, optional): UK region code or postcode
- **hours** (int, optional): Forecast hours ahead (default: 24)
- Returns forecast of carbon intensity

### get_generation_mix
- Returns current breakdown of electricity generation sources
- Includes renewable vs fossil fuel percentages

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

Use fastmcp's `@mcp.tool()` decorator with optional parameters:

```python
from fastmcp import FastMCP
import httpx

mcp = FastMCP("carbon-intensity")

@mcp.tool()
async def get_current_intensity(region: str | None = None) -> str:
    # Your implementation here
    pass
```

## Testing

Test with different UK postcodes or regions:
- London: "SW1"
- Scotland: "14"
- Wales: "15"

## Resources

- [Carbon Intensity API Documentation](https://carbon-intensity.github.io/api-definitions/)
- [MCP Documentation](https://modelcontextprotocol.io/)

## Example Usage

Ask Claude: "What's the current carbon intensity in London?" or "When is the best time to use electricity today based on carbon intensity?"
