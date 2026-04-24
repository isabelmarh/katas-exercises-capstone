def summarize_messages(messages: list[tuple[str, str]]) -> str:
    """Replace with model-based summarization when memory grows."""
    return "\n".join(f"{role}: {content}" for role, content in messages)
