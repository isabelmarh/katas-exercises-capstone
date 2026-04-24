from mcp.server.fastmcp import FastMCP
import httpx

mcp = FastMCP("currency-exchange")
http_client = httpx.Client()


# TODO: Implement get_exchange_rate tool
# Hint: Call https://open.er-api.com/v6/latest/{from_currency}
# Extract the rate for to_currency from the rates dict
@mcp.tool()
async def get_exchange_rate(from_currency: str, to_currency: str) -> str:
    """Get exchange rate from one currency to another."""
    try:
        async with httpx.AsyncClient() as client:
            url = f"https://open.er-api.com/v6/latest/{from_currency}"
            response = await client.get(url)
            response.raise_for_status()
            data = response.json()
            rate = data["rates"].get(to_currency)
            if rate is None:
                return f"Currency {to_currency} not found."
            return f"Exchange rate from {from_currency} to {to_currency}: {rate:.4f}"
    except Exception as e:
        return f"Error fetching exchange rate: {e}"


# TODO: Implement convert_currency tool
# Hint: Get the exchange rate and multiply by the amount
# Format the result nicely with 2 decimal places
@mcp.tool()
async def convert_currency(amount: float, from_currency: str, to_currency: str) -> str:
    """Convert an amount from one currency to another."""
    try:
        async with httpx.AsyncClient() as client:
            url = f"https://open.er-api.com/v6/latest/{from_currency}"
            response = await client.get(url)
            response.raise_for_status()
            data = response.json()
            rate = data["rates"].get(to_currency)
            if rate is None:
                return f"Currency {to_currency} not found."
            converted_amount = amount * rate
            return f"{amount:.2f} {from_currency} is approximately {converted_amount:.2f} {to_currency} at the current exchange rate."
    except Exception as e:
        return f"Error converting currency: {e}"


# TODO: Implement list_currencies tool
# Hint: Call the API with any base currency and extract all keys from rates dict
@mcp.tool()
async def list_currencies() -> str:
    """List all available currencies."""
    try:
        async with httpx.AsyncClient() as client:
            url = "https://open.er-api.com/v6/latest/USD"
            response = await client.get(url)
            response.raise_for_status()
            data = response.json()
            currencies = sorted(data["rates"].keys())
            return "Available currencies: " + ", ".join(currencies)
    except Exception as e:
        return f"Error fetching currency list: {e}"

if __name__ == "__main__":
    mcp.run()