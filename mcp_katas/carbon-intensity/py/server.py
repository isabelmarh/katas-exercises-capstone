from mcp.server.fastmcp import FastMCP
import httpx

mcp = FastMCP("carbon-intensity")


# TODO: Implement get_current_intensity tool
# Hint: Call https://api.carbonintensity.org.uk/intensity for national data
# Or https://api.carbonintensity.org.uk/regional/postcode/{postcode} for regional


# TODO: Implement get_intensity_forecast tool
# Hint: Use the /intensity endpoint and parse the data array for future periods


# TODO: Implement get_generation_mix tool
# Hint: Call https://api.carbonintensity.org.uk/generation
# Parse the generationmix array
