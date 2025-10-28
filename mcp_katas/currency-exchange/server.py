from mcp.server.fastmcp import FastMCP
import httpx

mcp = FastMCP("currency-exchange")


# TODO: Implement get_exchange_rate tool
# Hint: Call https://open.er-api.com/v6/latest/{from_currency}
# Extract the rate for to_currency from the rates dict


# TODO: Implement convert_currency tool
# Hint: Get the exchange rate and multiply by the amount
# Format the result nicely with 2 decimal places


# TODO: Implement list_currencies tool
# Hint: Call the API with any base currency and extract all keys from rates dict
