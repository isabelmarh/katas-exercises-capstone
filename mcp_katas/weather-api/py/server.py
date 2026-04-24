from mcp.server.fastmcp import FastMCP
import httpx

mcp = FastMCP("weather-api")
http_client = httpx.Client()

# TODO: Implement get_weather tool
# Hint: Use httpx to call https://wttr.in/{location}?format=j1
# Return current temperature, conditions, humidity, wind speed
@mcp.tool()
async def get_weather(
    location: str,
    units: str = "metric",
    ) -> str:
    """Get weather for a city
    Args: location: City name to get weather for
        units: "metric" or "imperial" (default: "metric")
    """
    # Your implementation
    try:
        async with httpx.AsyncClient() as client:
            url = f"https://wttr.in/{location}?format=j1"
            response = await client.get(url)
            response.raise_for_status()
            data = response.json()
            current_condition = data["current_condition"][0]
            temp = current_condition["temp_C"] if units == "metric" else current_condition["temp_F"]
            conditions = current_condition["weatherDesc"][0]["value"]
            humidity = current_condition["humidity"]
            wind_speed = current_condition["windspeedKmph"] if units == "metric" else current_condition["windspeedMiles"]
            return f"Current weather in {location}: {temp}°{'C' if units == 'metric' else 'F'}, \
{conditions}, Humidity: {humidity}%, Wind Speed: {wind_speed} {'km/h' if units == 'metric' else 'mph'}"
    except Exception as e:
        return f"Error fetching weather for {location}: {e}" 

if __name__ == "__main__":
    mcp.run()


@mcp.tool()
async def get_forecast(
    location: str,
    days: int = 3,
    units: str = "metric",
) -> str:
    """Get weather forecast for upcoming days

    Args:
        location: City name to get forecast for
        days: Number of days (1-3, default: 3)
        units: "metric" or "imperial" (default: "metric")
    """
    try:
        async with httpx.AsyncClient() as client:
            url = f"https://wttr.in/{location}?format=j1"
            response = await client.get(url, timeout=10.0)
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
    except Exception as e:
        return f"Error fetching forecast for {location}: {e}"
