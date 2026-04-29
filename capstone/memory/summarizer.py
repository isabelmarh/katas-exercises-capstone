def summarize_messages(messages: list[tuple[str, str]]) -> str:
    """Create a compact summary of recent conversation context."""
    recent = messages[-3:]
    lines: list[str] = []
    for role, content in recent:
        compact = " ".join(content.split())
        if len(compact) > 120:
            compact = f"{compact[:117]}..."
        lines.append(f"{role}: {compact}")
    return "\n".join(lines)


def format_preferences(preferences: dict[str, str]) -> str:
    if not preferences:
        return ""
    return "\n".join(f"- {key.replace('_', ' ')}: {value}" for key, value in preferences.items())


def summarize_episode(
    user_query: str, assistant_response: str
) -> tuple[str, list[str], float]:
    """Create a compact episodic memory record from one interaction."""
    normalized_query = " ".join(user_query.split())
    normalized_response = " ".join(assistant_response.split())
    summary = (
        f"User asked: {normalized_query[:100]}. "
        f"Assistant recommended: {normalized_response[:180]}"
    )

    tags: list[str] = []
    lowered = f"{normalized_query} {normalized_response}".lower()
    for candidate in ("backend", "platform", "ai", "remote", "startup", "leadership"):
        if candidate in lowered:
            tags.append(candidate)

    relevance_score = 0.7 if tags else 0.5
    return summary, tags, relevance_score
