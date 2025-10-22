# Model Context Protocol
### Building AI Agent Tools with MCP

Ben O'Mahony
@benomahony

---

# What is MCP?

**Model Context Protocol** - An open protocol for connecting AI assistants to external tools and data sources.

Think of it as a standardized way for AI models to:
- Access real-time data
- Use external APIs
- Interact with local tools
- Connect to your systems

---

# The Problem MCP Solves

**Before MCP:**
- Every AI tool integration was custom
- Duplicated effort across providers
- No standardization
- Hard to share and reuse

**With MCP:**
- Write once, use anywhere
- Standard protocol
- Works with Claude, ChatGPT, and more
- Easy to share and compose

---

# MCP Architecture

```
┌─────────────┐
│  AI Model   │
│  (Claude)   │
└──────┬──────┘
       │ MCP Protocol
       ▼
┌─────────────┐
│ MCP Server  │  ← You build this!
│             │
│ - Tools     │
│ - Resources │
│ - Prompts   │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  External   │
│    APIs     │
└─────────────┘
```

---

# Core Concepts

**Tools**: Functions the AI can call
- Weather lookup
- Database queries
- File operations

**Resources**: Data the AI can read
- Files
- API responses
- Database records

**Prompts**: Reusable prompt templates
- Common workflows
- Best practices

---

# Why Build MCP Servers?

**Extend AI Capabilities**
- Give AI access to real-time data
- Enable action-taking beyond text generation

**Reusable Components**
- Build once, use in multiple AI tools
- Share with the community

**Type-Safe & Reliable**
- Structured inputs and outputs
- Clear contracts between AI and tools

---

# Enter FastMCP

Building MCP servers the easy way:

```python
from fastmcp import FastMCP

mcp = FastMCP("my-server")

@mcp.tool()
async def get_weather(city: str) -> str:
    """Get weather for a city"""
    # Your implementation
    return f"Weather in {city}: Sunny"

if __name__ == "__main__":
    mcp.run()
```

That's it! No boilerplate, just tools.

---

# FastMCP Features

**Simple Decorators**
- `@mcp.tool()` for functions
- `@mcp.resource()` for data
- Automatic schema generation

**Type Safety**
- Python type hints → JSON schema
- Runtime validation
- Clear error messages

**Async First**
- Built for async/await
- HTTP client support
- Efficient I/O

---

# Building Your First Tool

```python
from fastmcp import FastMCP
import httpx

mcp = FastMCP("weather")

@mcp.tool()
async def get_weather(location: str) -> str:
    """Get current weather for a location"""
    async with httpx.AsyncClient() as client:
        url = f"https://wttr.in/{location}?format=j1"
        response = await client.get(url)
        data = response.json()
        
        temp = data["current_condition"][0]["temp_C"]
        desc = data["current_condition"][0]["weatherDesc"][0]["value"]
        
        return f"{location}: {temp}°C, {desc}"
```

---

# Tool Parameters

**Required Parameters**
```python
@mcp.tool()
async def convert(amount: float, from_curr: str, to_curr: str) -> str:
    ...
```

**Optional Parameters**
```python
@mcp.tool()
async def forecast(location: str, days: int = 3) -> str:
    ...
```

**Type Annotations = Schema**
- Python types become JSON schema
- AI knows what to send
- Automatic validation

---

# Testing Your Server

**Use MCP Inspector**
```bash
npx @modelcontextprotocol/inspector uv run server.py
```

Interactive UI to:
- See available tools
- Test with different inputs
- View responses
- Debug issues

---

# Connecting to Claude Desktop

Add to config (`~/Library/Application Support/Claude/claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "weather": {
      "command": "uv",
      "args": [
        "--directory",
        "/path/to/your/server",
        "run",
        "server.py"
      ]
    }
  }
}
```

Restart Claude Desktop and your tools are available!

---

# MCP Katas

Practice building MCP servers with real APIs:

**🌤️ Weather API** - Get weather data
**🌍 Carbon Intensity** - UK electricity data
**💱 Currency Exchange** - Convert currencies  
**🎲 Random Facts** - Jokes, quotes, cat facts

Each kata provides:
- Skeleton code with TODOs
- API documentation
- Implementation hints

---

# Kata Structure

```
mcp_katas/<kata-name>/
├── README.md         # Challenge & API docs
├── server.py         # TODO: Implement here
└── pyproject.toml    # Dependencies
```

Learn by doing:
1. Read the challenge
2. Implement the TODOs
3. Test with MCP inspector
4. Connect to Claude Desktop

---

# Example: Weather Kata

**Challenge**: Build a weather MCP server

**Your Task**:
```python
from fastmcp import FastMCP

mcp = FastMCP("weather-api")

# TODO: Implement get_weather tool
# Hint: Use wttr.in API

# TODO: Implement get_forecast tool
# Hint: Parse weather array from API
```

Start simple, iterate, test!

---

# Learning Path

**1. Random Facts** (Easy)
- Simple API calls
- No parameters
- Pure functions

**2. Weather API** (Medium)
- Parameters and defaults
- Data parsing
- Unit conversion

**3. Carbon Intensity** (Medium)
- Optional parameters
- Business logic
- Recommendations

**4. Currency Exchange** (Advanced)
- Multiple tools
- Error handling
- Data transformation

---

# Best Practices

**Keep Tools Focused**
- One tool, one job
- Clear, descriptive names
- Helpful docstrings

**Handle Errors Gracefully**
```python
try:
    response = await client.get(url)
    response.raise_for_status()
except httpx.HTTPError as e:
    return f"Error: {e}"
```

**Format Output Well**
- Human-readable strings
- Structured information
- Include units and context

---

# Real-World Use Cases

**Development Tools**
- Git operations
- Database queries
- API testing

**Business Systems**
- CRM access
- Analytics data
- Reporting tools

**Data Sources**
- Weather
- Financial data
- News feeds

**Local Files**
- Search
- Read/write
- Analysis

---

# MCP Ecosystem

**Official SDK**: Python, TypeScript
**FastMCP**: Simplified Python library
**Community Servers**: Growing library of tools
**Claude Desktop**: First-class integration
**VS Code**: Coming soon

Build once, use everywhere!

---

# Security Considerations

**Read-Only by Default**
- Start with GET operations
- No destructive actions
- Safe for AI exploration

**Validate Inputs**
- Type hints help
- Add custom validation
- Sanitize user data

**Scope Appropriately**
- Limit file access
- Rate limit APIs
- Log operations

---

# Getting Started

```bash
# Clone the repo
git clone <repo-url>
cd ai-agent-katas/mcp_katas

# Pick a kata
cd weather-api

# Install dependencies
uv sync

# Implement the TODOs in server.py

# Test it
npx @modelcontextprotocol/inspector uv run server.py
```

---

# Key Takeaways

✅ MCP standardizes AI-tool integration

✅ FastMCP makes building servers simple

✅ Katas provide hands-on practice

✅ Type safety from Python to protocol

✅ Works with Claude Desktop out of the box

✅ Build once, use across AI platforms

---

# Resources

**MCP Katas**: `/mcp_katas` in this repo

**FastMCP**: https://github.com/jlowin/fastmcp

**MCP Docs**: https://modelcontextprotocol.io/

**Claude Desktop**: https://claude.ai/download

**Questions?**

---

# Let's Build Some Servers! 🚀

```bash
cd mcp_katas
uv sync
# Pick a kata and start coding!
```
