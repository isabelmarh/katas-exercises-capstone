# MCP Kata Solutions

Building step by step

---

# Today

**Kata 1**: Random Facts (Easy)
**Kata 2**: Weather API (Medium)

Live coding walkthrough

---

# Kata 1: Random Facts

4 tools, 4 APIs, no parameters

---

# What We're Building

- Cat facts
- Useless facts
- Jokes
- Quotes

---

# Start: Empty File

```python

```

---

# Import MCP

```python
from mcp.server.fastmcp import FastMCP
```

---

# Import HTTP Client

```python
from mcp.server.fastmcp import FastMCP
import httpx
```

---

# Create Server

```python
from mcp.server.fastmcp import FastMCP
import httpx

mcp = FastMCP("random-facts")
```

---

# First Tool: Start

```python
@mcp.tool()
async def get_cat_fact():
```

---

# Add Return Type

```python
@mcp.tool()
async def get_cat_fact() -> str:
```

---

# Add Docstring

```python
@mcp.tool()
async def get_cat_fact() -> str:
    """Get a random fact about cats"""
```

---

# HTTP Client Context

```python
@mcp.tool()
async def get_cat_fact() -> str:
    """Get a random fact about cats"""
    async with httpx.AsyncClient() as client:
```

---

# Make Request

```python
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://catfact.ninja/fact"
        )
```

---

# Check Status

```python
        response = await client.get(
            "https://catfact.ninja/fact"
        )
        response.raise_for_status()
```

---

# Parse JSON

```python
        response.raise_for_status()
        data = response.json()
```

---

# Return Fact

```python
        data = response.json()
        return data['fact']
```

---

# Add Emoji

```python
        data = response.json()
        return f"🐱 Cat Fact: {data['fact']}"
```

---

# First Tool Done!

```python
@mcp.tool()
async def get_cat_fact() -> str:
    """Get a random fact about cats"""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://catfact.ninja/fact"
        )
        response.raise_for_status()
        data = response.json()
        return f"🐱 Cat Fact: {data['fact']}"
```

---

# Test It

```bash
mcp dev server.py
```

Opens inspector automatically!

---

# See Your Tool

Tool name: `get_cat_fact`
Description: "Get a random fact about cats"
Click "Call"
See result!

---

# Second Tool: Useless Facts

Same pattern, different API

---

# Copy Structure

```python
@mcp.tool()
async def get_useless_fact() -> str:
    """Get a random useless but interesting fact"""
    async with httpx.AsyncClient() as client:
```

---

# Different URL

```python
        response = await client.get(
            "https://uselessfacts.jsph.pl/api/v2/facts/random"
        )
        response.raise_for_status()
        data = response.json()
```

---

# Different Field

```python
        data = response.json()
        return f"💡 Useless Fact: {data['text']}"
```

Not `['fact']` - it's `['text']`!

---

# Third Tool: Jokes

This one has structure

---

# Start Tool

```python
@mcp.tool()
async def get_joke() -> str:
    """Get a random joke"""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://official-joke-api.appspot.com/random_joke"
        )
        response.raise_for_status()
        data = response.json()
```

---

# Two Fields

```python
        data = response.json()
        setup = data['setup']
        punchline = data['punchline']
```

---

# Format Together

```python
        setup = data['setup']
        punchline = data['punchline']
        
        return f"😄 {setup}\n\n{punchline}"
```

---

# Fourth Tool: Quotes

Two fields again

---

# Setup

```python
@mcp.tool()
async def get_quote() -> str:
    """Get a random inspirational quote"""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://api.quotable.io/random"
        )
        response.raise_for_status()
        data = response.json()
```

---

# Extract Fields

```python
        data = response.json()
        content = data['content']
        author = data['author']
```

---

# Format Nicely

```python
        content = data['content']
        author = data['author']
        
        return f'✨ "{content}"\n\n— {author}'
```

---

# All 4 Tools Done!

Run again:

```bash
mcp dev server.py
```

Test each tool!

---

# Complete Code

```python
from mcp.server.fastmcp import FastMCP
import httpx

mcp = FastMCP("random-facts")

@mcp.tool()
async def get_cat_fact() -> str:
    """Get a random fact about cats"""
    async with httpx.AsyncClient() as client:
        response = await client.get("https://catfact.ninja/fact")
        response.raise_for_status()
        data = response.json()
        return f"🐱 Cat Fact: {data['fact']}"

@mcp.tool()
async def get_useless_fact() -> str:
    """Get a random useless but interesting fact"""
    async with httpx.AsyncClient() as client:
        url = "https://uselessfacts.jsph.pl/api/v2/facts/random"
        response = await client.get(url)
        response.raise_for_status()
        data = response.json()
        return f"💡 Useless Fact: {data['text']}"
```

---

# Complete Code (2/3)

```python
@mcp.tool()
async def get_joke() -> str:
    """Get a random joke"""
    async with httpx.AsyncClient() as client:
        url = "https://official-joke-api.appspot.com/random_joke"
        response = await client.get(url)
        response.raise_for_status()
        data = response.json()
        return f"😄 {data['setup']}\n\n{data['punchline']}"

@mcp.tool()
async def get_quote() -> str:
    """Get a random inspirational quote"""
    async with httpx.AsyncClient() as client:
        response = await client.get("https://api.quotable.io/random")
        response.raise_for_status()
        data = response.json()
        return f'✨ "{data["content"]}"\n\n— {data["author"]}'
```

---

# What We Learned

✅ Basic tool structure
✅ HTTP requests with httpx
✅ JSON parsing
✅ String formatting
✅ Multiple tools in one server
✅ Testing with `mcp dev`

---

# Kata 2: Weather API

Now with parameters!

---

# What We're Building

- `get_weather(location, units)`
- `get_forecast(location, days, units)`

---

# New: Parameters

Tools can take inputs

---

# Start Fresh

```python
from mcp.server.fastmcp import FastMCP
import httpx

mcp = FastMCP("weather-api")
```

---

# Tool Signature

```python
@mcp.tool()
async def get_weather(location: str) -> str:
```

Required parameter: `location`

---

# Add Optional Parameter

```python
@mcp.tool()
async def get_weather(
    location: str, 
    units: str = "metric"
) -> str:
```

Default value = optional

---

# Docstring

```python
@mcp.tool()
async def get_weather(
    location: str,
    units: str = "metric"
) -> str:
    """Get current weather
    
    Args:
        location: City name
        units: 'metric' or 'imperial'
    """
```

---

# Build URL

```python
    async with httpx.AsyncClient() as client:
        url = f"https://wttr.in/{location}?format=j1"
```

Location goes in URL!

---

# Make Request

```python
        url = f"https://wttr.in/{location}?format=j1"
        response = await client.get(url)
        response.raise_for_status()
        data = response.json()
```

---

# Explore Response

```json
{
  "current_condition": [{
    "temp_C": "15",
    "temp_F": "59",
    "weatherDesc": [{"value": "Cloudy"}],
    "humidity": "72"
  }]
}
```

---

# Navigate to Current

```python
        data = response.json()
        current = data["current_condition"][0]
```

---

# Choose Temp Field

```python
        current = data["current_condition"][0]
        
        if units == "metric":
            temp_key = "temp_C"
        else:
            temp_key = "temp_F"
```

---

# Get Temperature

```python
        if units == "metric":
            temp_key = "temp_C"
            unit_symbol = "°C"
        else:
            temp_key = "temp_F"
            unit_symbol = "°F"
        
        temp = current[temp_key]
```

---

# Get Other Fields

```python
        temp = current[temp_key]
        conditions = current["weatherDesc"][0]["value"]
        humidity = current["humidity"]
        wind = current["windspeedKmph"]
```

---

# Format Result

```python
        return f"""Weather in {location}:
Temperature: {temp}{unit_symbol}
Conditions: {conditions}
Humidity: {humidity}%
Wind: {wind} km/h"""
```

---

# First Tool Complete!

```python
@mcp.tool()
async def get_weather(
    location: str,
    units: str = "metric"
) -> str:
    """Get current weather"""
    async with httpx.AsyncClient() as client:
        url = f"https://wttr.in/{location}?format=j1"
        response = await client.get(url)
        response.raise_for_status()
        data = response.json()
        
        current = data["current_condition"][0]
        temp_key = "temp_C" if units == "metric" else "temp_F"
        unit = "°C" if units == "metric" else "°F"
        
        return f"""Weather in {location}:
{current[temp_key]}{unit}
{current["weatherDesc"][0]["value"]}
Humidity: {current["humidity"]}%"""
```

---

# Test It

```bash
mcp dev server.py
```

Try different locations and units!

---

# Test Different Inputs

```
get_weather("London")
get_weather("Tokyo", "metric")
get_weather("NYC", "imperial")
```

---

# Forecast: More Parameters

```python
@mcp.tool()
async def get_forecast(
    location: str,
    days: int = 3,
    units: str = "metric"
) -> str:
```

Three parameters now!

---

# Same API Call

```python
    async with httpx.AsyncClient() as client:
        url = f"https://wttr.in/{location}?format=j1"
        response = await client.get(url)
        response.raise_for_status()
        data = response.json()
```

---

# Different Data Section

```python
        data = response.json()
        forecast = data["weather"]
```

Array of forecast days

---

# Choose Temp Keys

```python
        forecast = data["weather"]
        
        temp_key = "maxtempC" if units == "metric" else "maxtempF"
        min_key = "mintempC" if units == "metric" else "mintempF"
        unit = "°C" if units == "metric" else "°F"
```

---

# Start Result String

```python
        result = f"Forecast for {location}:\n\n"
```

---

# Loop Through Days

```python
        result = f"Forecast for {location}:\n\n"
        
        for day_data in forecast[:days]:
```

Slice array with `[:days]`!

---

# Extract Day Data

```python
        for day_data in forecast[:days]:
            date = day_data["date"]
            max_temp = day_data[temp_key]
            min_temp = day_data[min_key]
```

---

# Build Result

```python
            result += f"""Date: {date}
High: {max_temp}{unit}
Low: {min_temp}{unit}
---
"""
```

---

# Return It

```python
        for day_data in forecast[:days]:
            date = day_data["date"]
            max_temp = day_data[temp_key]
            min_temp = day_data[min_key]
            
            result += f"""Date: {date}
High: {max_temp}{unit}
Low: {min_temp}{unit}
---
"""
        
        return result
```

---

# Forecast Complete!

```python
@mcp.tool()
async def get_forecast(
    location: str,
    days: int = 3,
    units: str = "metric"
) -> str:
    """Get weather forecast"""
    async with httpx.AsyncClient() as client:
        url = f"https://wttr.in/{location}?format=j1"
        response = await client.get(url)
        response.raise_for_status()
        data = response.json()
        
        temp_key = "maxtempC" if units == "metric" else "maxtempF"
        min_key = "mintempC" if units == "metric" else "mintempF"
        unit = "°C" if units == "metric" else "°F"
        
        result = f"Forecast for {location}:\n\n"
        for day in data["weather"][:days]:
            result += f"Date: {day['date']}\n"
            result += f"High: {day[temp_key]}{unit}\n"
            result += f"Low: {day[min_key]}{unit}\n---\n"
        return result
```

---

# Test Both Tools

```bash
mcp dev server.py
```

Try all combinations!

---

# Test Cases

```
get_weather("Paris")
get_weather("Berlin", "imperial")
get_forecast("Tokyo")
get_forecast("London", 1)
get_forecast("NYC", 2, "imperial")
```

---

# What We Learned

✅ Required parameters
✅ Optional parameters with defaults
✅ Using parameters in URLs
✅ Conditional logic for options
✅ Looping through arrays
✅ Building strings incrementally
✅ Using `mcp dev` for testing

---

# Key Pattern

```python
@mcp.tool()
async def tool(param: str, opt: str = "default") -> str:
    """Description"""
    async with httpx.AsyncClient() as client:
        url = f"https://api.com/{param}"
        response = await client.get(url)
        data = response.json()
        
        # Process data
        # Use opt parameter
        # Format result
        
        return result
```

---

# Add Error Handling

```python
    try:
        async with httpx.AsyncClient() as client:
            # ... your code
    except httpx.HTTPError as e:
        return f"Error: {e}"
```

---

# Add Timeouts

```python
        response = await client.get(
            url, 
            timeout=10.0
        )
```

---

# Development Workflow

```bash
# Edit server.py
# Save

# Test
mcp dev server.py

# Edit more
# Save

# Test again
mcp dev server.py
```

Fast iteration!

---

# Connect to Claude Desktop

Config file:
`~/Library/Application Support/Claude/claude_desktop_config.json`

---

# Add Your Server

```json
{
  "mcpServers": {
    "weather": {
      "command": "mcp",
      "args": ["dev", "/path/to/server.py"]
    }
  }
}
```

---

# Restart Claude

Your tools appear in Claude!

Ask: "What's the weather in Paris?"

---

# Recap: Random Facts

4 simple tools
No parameters
Different APIs
JSON parsing
`mcp dev` for testing

---

# Recap: Weather

2 complex tools
Multiple parameters
Conditional logic
Array processing
Same testing workflow

---

# Next Steps

Try remaining katas:
- Carbon Intensity
- Currency Exchange

Same pattern, new APIs!

---

# Practice More

Build your own servers
Connect to Claude Desktop
Use in real workflows

---

# The MCP CLI

```bash
# Test your server
mcp dev server.py

# Install as tool
mcp install server.py

# List installed servers
mcp list
```

---

# Resources

`/mcp_katas` - Practice exercises
`modelcontextprotocol.io` - Official docs
MCP Python SDK - Official library

---

# You've Got This! 🚀

Start simple
Build incrementally
Test with `mcp dev`
Ship to Claude Desktop
