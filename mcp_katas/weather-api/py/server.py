from mcp.server.fastmcp import FastMCP
import httpx

mcp = FastMCP("weather-api")


# TODO: Implement get_weather tool
# Hint: Use httpx to call https://wttr.in/{location}?format=j1
# Return current temperature, conditions, humidity, wind speed


# TODO: Implement get_forecast tool  
# Hint: Parse the weather array from the API response
# Return forecast for the requested number of days
