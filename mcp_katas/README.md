# MCP Server Katas

Practice building Model Context Protocol (MCP) servers with real-world APIs using fastmcp.

## What are MCP Servers?

MCP servers expose tools and resources that AI agents can use. They bridge the gap between AI models and external systems, APIs, and data sources.

## Available Katas

### 🌤️ Weather API
Build an MCP server using the free wttr.in weather API.
- Get current weather for any location
- Retrieve multi-day forecasts
- Support metric and imperial units

### 🌍 Carbon Intensity
Create an MCP server for UK electricity carbon intensity data.
- Check current carbon intensity
- Get generation mix (renewable vs fossil)
- Find best times to use electricity

### 💱 Currency Exchange
Build a currency conversion MCP server.
- Get real-time exchange rates
- Convert between currencies
- List supported currencies

### 🎲 Random Facts
Fun MCP server aggregating multiple fact APIs.
- Cat facts
- Useless facts
- Programming jokes
- Inspirational quotes

## Getting Started

Each kata provides:
- `README.md` - Challenge description and API docs
- `server.py` - Skeleton code with TODOs for you to implement
- `pyproject.toml` - Dependencies

### Implementing a Kata

```bash
cd mcp_katas/<kata-name>
uv sync

# Edit server.py and implement the TODO sections

# Test your implementation
mcp dev server.py
```

This automatically opens the MCP inspector!

### Testing Your Implementation

Use the MCP CLI to test your tools:

```bash
mcp dev server.py
```

This opens an interactive inspector where you can test each tool!

### Using with Claude Desktop

Add to your Claude Desktop config (`~/Library/Application Support/Claude/claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "weather": {
      "command": "mcp",
      "args": [
        "dev",
        "/Users/benomahony/thoughtworks/ai-agent-katas/mcp_katas/weather-api/server.py"
      ]
    }
  }
}
```

## Learning Path

1. **Start Simple**: Begin with `random-facts` - pure API calls, no parameters
2. **Add Complexity**: Move to `weather-api` - handle parameters and different units
3. **Business Logic**: Try `carbon-intensity` - interpret and recommend based on data
4. **Multiple Tools**: Build `currency-exchange` - coordinate between different operations

## FastMCP Patterns

All katas use the FastMCP API from the official MCP Python SDK:

```python
from mcp.server.fastmcp import FastMCP
import httpx

mcp = FastMCP("my-server")

@mcp.tool()
async def my_tool(param: str) -> str:
    """Tool description for the AI agent"""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"https://api.example.com/{param}")
        data = response.json()
        return f"Result: {data['field']}"
```

## Resources

- [FastMCP Documentation](https://github.com/jlowin/fastmcp)
- [MCP Documentation](https://modelcontextprotocol.io/)
- [Claude Desktop](https://claude.ai/download)

## Tips

- All APIs used are **free** with **no authentication** required
- Implement one tool at a time and test as you go
- Use the MCP inspector to verify your tools work correctly
- Read the API documentation carefully for response structure
- Add helpful descriptions to your @mcp.tool() decorated functions
