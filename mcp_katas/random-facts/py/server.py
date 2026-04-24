from mcp.server.fastmcp import FastMCP
import httpx

mcp = FastMCP("random-facts")
http_client = httpx.Client()

# TODO: Implement get_cat_fact tool
# Hint: Call https://catfact.ninja/fact and extract the 'fact' field
# Return with a fun emoji prefix
mcp = FastMCP("random-facts")
@mcp.tool()
async def get_cat_fact() -> str:
    """Get a random cat fact"""
    try:
        async with httpx.AsyncClient() as client:
            url = "https://catfact.ninja/fact"
            response = await client.get(url)
            response.raise_for_status()
            data = response.json()
            return f"🐱 Cat Fact: {data['fact']}"
    except Exception as e:
        return f"Error fetching cat fact: {e}"        

# TODO: Implement get_useless_fact tool
# Hint: Call https://uselessfacts.jsph.pl/api/v2/facts/random
# Extract the 'text' field
@mcp.tool()
async def get_useless_fact() -> str:
    """Get a random useless fact"""
    async with httpx.AsyncClient() as client:
        response = await client.get("https://uselessfacts.jsph.pl/api/v2/facts/random")
        response.raise_for_status()
        data = response.json()
        return f"🤪 Useless Fact: {data['text']}"

# TODO: Implement get_joke tool
# Hint: Call https://official-joke-api.appspot.com/random_joke
# Format with setup and punchline
@mcp.tool()
async def get_joke() -> str:
    """Get a random joke"""
    async with httpx.AsyncClient() as client:
        response = await client.get("https://official-joke-api.appspot.com/random_joke")
        response.raise_for_status()
        data = response.json()
        return f"😂 Joke: {data['setup']} - {data['punchline']}"


# TODO: Implement get_quote tool
# Hint: Call https://zenquotes.io/api/random
# Extract quote "q" and author "q" fields
@mcp.tool()
async def get_quote() -> str:
    """Get a random inspirational quote"""
    async with httpx.AsyncClient() as client:
        response = await client.get("https://zenquotes.io/api/random")
        response.raise_for_status()
        data = response.json()[0]
        return f"💡 Quote: \"{data['q']}\" - {data['a']}"


if __name__ == "__main__":
    mcp.run()
