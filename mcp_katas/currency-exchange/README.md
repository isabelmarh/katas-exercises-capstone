# Currency Exchange MCP Server

## Goal

Build an MCP server that provides real-time currency exchange rates using the exchangerate-api.com free tier.

## Challenge

Your MCP server should expose tools to:
- Get exchange rates for a currency
- Convert amounts between currencies
- Get a list of supported currencies

## API Information

**ExchangeRate-API** (free tier):
- Base URL: `https://open.er-api.com/v6/latest/{base_currency}`
- No API key required for basic usage
- 1,500 requests/month free tier
- Real-time exchange rates

Example request:
```bash
curl "https://open.er-api.com/v6/latest/USD"
```

## MCP Server Structure

Your server should expose these tools:

### get_exchange_rate
- **from_currency** (string): Source currency code (e.g., "USD")
- **to_currency** (string): Target currency code (e.g., "EUR")
- Returns the exchange rate

### convert_currency
- **amount** (number): Amount to convert
- **from_currency** (string): Source currency code
- **to_currency** (string): Target currency code
- Returns converted amount with rate

### list_currencies
- Returns list of supported currency codes

## Getting Started

```bash
# Install dependencies
uv sync

# Run the MCP server
uv run server.py
```

## Resources

- [ExchangeRate-API Documentation](https://www.exchangerate-api.com/docs/free)
- [MCP Documentation](https://modelcontextprotocol.io/)
