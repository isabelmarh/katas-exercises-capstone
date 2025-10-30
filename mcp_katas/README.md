# MCP Server Katas

Practice building Model Context Protocol (MCP) servers with real-world APIs in Python and .NET.

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

Each kata contains a `README.md` with the challenge description and API docs. 

Within each kata, there are folders for Python and C# . 

Python folder structure:

- `server.py` - Skeleton code with TODOs for you to implement
- `pyproject.toml` - Dependencies

C# folder structure:
- `Server.cs` - Skeleton code with TODOs for you to implement
- `Project.csproj` - Project SDK / dependencies


### Implementing a Kata

Python:
```bash
# Navigate to the kata
cd <kata-name>/py

# Sync dependencies
uv sync

# Edit server.py and implement the TODO sections

# Test your implementation
# This automatically opens the MCP inspector!
mcp dev server.py
```

C#:
```bash
# Navigate to the kata
cd <kata-name>/cs

# Install dependencies
dotnet restore

# Run the kata project
dotnet run

# Open the MCP Inspector to test your MCP Server
# Note: Requires NodeJS to be installed - see https://nodejs.org/download
npx @modelcontextprotocol/inspector
```



### Testing Your Implementation

Use the MCP CLI to test your tools:

Python:
```bash
# This automatically opens the MCP inspector
mcp dev server.py
```

NodeJS (suitable for C# developers):

> Note: Requires NodeJS to be installed - see https://nodejs.org/download

```bash
# This automatically opens the MCP inspector
npx @modelcontextprotocol/inspector
```

This opens an interactive inspector where you can test each tool!

### Using with Claude Desktop

Add to your Claude Desktop config (`~/Library/Application Support/Claude/claude_desktop_config.json`):

Python:
```json
{
  "mcpServers": {
    "weather": {
      "command": "mcp",
      "args": [
        "dev",
        "<path-to-katas-repository>/mcp_katas/weather-api/py/server.py"
      ]
    }
  }
}
```

C#:
```json
{
  "mcpServers": {
    "weather": {
      "command": "dotnet",
      "args": [
        "run",
        "--project",
        "<path-to-katas-repository>/mcp_katas/weather-api/cs/Project.csproj"
      ]
    }
  }
}

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

- [MCP Documentation](https://modelcontextprotocol.io/)
- [FastMCP Documentation](https://github.com/jlowin/fastmcp)
- [C# MCP Documentation](https://github.com/modelcontextprotocol/csharp-sdk)
- [Claude Desktop](https://claude.ai/download)

## Tips

- All APIs used are **free** with **no authentication** required
- Implement one tool at a time and test as you go
- Use the MCP inspector to verify your tools work correctly
- Read the API documentation carefully for response structure
- Add helpful descriptions to your @mcp.tool() decorated functions
