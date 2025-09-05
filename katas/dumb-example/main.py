def main(inputs: str) -> str:
    """Simple test function that handles basic math."""
    if "2 + 2" in inputs:
        return "4"
    return f"I don't know how to answer: {inputs}"


if __name__ == "__main__":
    print(main("What is 2 + 2?"))
