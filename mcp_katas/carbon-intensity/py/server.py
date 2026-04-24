from mcp.server.fastmcp import FastMCP
import httpx

mcp = FastMCP("carbon-intensity")
http_client = httpx.Client()

# TODO: Implement get_current_intensity tool
# Hint: Call https://api.carbonintensity.org.uk/intensity for national data
# Or https://api.carbonintensity.org.uk/regional/postcode/{postcode} for regional
@mcp.tool()
async def get_current_intensity(region: str | None = None) -> str:
    """Get current carbon intensity. If region is provided (as UK outcode like SW1A, OX1, M1), get regional intensity."""
    url = "https://api.carbonintensity.org.uk/intensity"
    if region:
        url = f"https://api.carbonintensity.org.uk/regional/postcode/{region}"
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            response.raise_for_status()
            data = response.json()
            if region:
                region_data = data["data"][0]
                period = region_data["data"][0]
                intensity = period["intensity"]["forecast"]
                index = period["intensity"]["index"]
                return f"Carbon intensity for {region_data['shortname']} ({region}): {intensity} gCO2/kWh ({index})"
            else:
                intensity = data["data"][0]["intensity"]
                return f"National carbon intensity: forecast={intensity['forecast']} gCO2/kWh, index={intensity['index']}"
    except Exception as e:
        return f"Error fetching carbon intensity: {e}"


# TODO: Implement get_intensity_forecast tool
# Hint: Use the /intensity endpoint and parse the data array for future periods
@mcp.tool()
async def get_intensity_forecast(region: str | None = None) -> str: 
    """Get carbon intensity forecast for the next 24 hours. If region is provided (as UK outcode like SW1A, OX1, M1), get regional forecast."""
    url = "https://api.carbonintensity.org.uk/intensity"
    if region:
        url = f"https://api.carbonintensity.org.uk/regional/postcode/{region}"
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            response.raise_for_status()
            data = response.json()
            forecast_str = ""
            if region:
                region_data = data["data"][0]
                forecast_str += f"Carbon intensity forecast for {region_data['shortname']} ({region}):\n"
                for period in region_data["data"]:
                    time = period["from"]
                    intensity = period["intensity"]["forecast"]
                    index = period["intensity"]["index"]
                    forecast_str += f"{time}: {intensity} gCO2/kWh ({index})\n"
            else:
                forecast_str += "National carbon intensity forecast:\n"
                for period in data["data"]:
                    time = period["from"]
                    intensity = period["intensity"]["forecast"]
                    index = period["intensity"]["index"]
                    forecast_str += f"{time}: {intensity} gCO2/kWh ({index})\n"
            return forecast_str
    except Exception as e:
        return f"Error fetching carbon intensity forecast: {e}"


# TODO: Implement get_generation_mix tool
# Hint: Call https://api.carbonintensity.org.uk/generation
# Parse the generationmix array
@mcp.tool()
async def get_generation_mix() -> str:
    """Get current electricity generation mix in the UK."""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("https://api.carbonintensity.org.uk/generation")
            response.raise_for_status()
            data = response.json()
            mix_str = "Current UK electricity generation mix:\n"
            for fuel in data["data"]["generationmix"]:
                mix_str += f"{fuel['fuel']}: {fuel['perc']}%\n"
            return mix_str
    except Exception as e:
        return f"Error fetching generation mix: {e}"

if __name__ == "__main__":
    mcp.run()
