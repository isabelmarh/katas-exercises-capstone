from fastmcp import FastMCP

mcp = FastMCP("random-facts")


# TODO: Implement get_cat_fact tool
# Hint: Call https://catfact.ninja/fact and extract the 'fact' field
# Return with a fun emoji prefix


# TODO: Implement get_useless_fact tool  
# Hint: Call https://uselessfacts.jsph.pl/api/v2/facts/random
# Extract the 'text' field


# TODO: Implement get_joke tool
# Hint: Call https://official-joke-api.appspot.com/random_joke
# Format with setup and punchline


# TODO: Implement get_quote tool
# Hint: Call https://api.quotable.io/random
# Extract content and author fields


if __name__ == "__main__":
    mcp.run()
