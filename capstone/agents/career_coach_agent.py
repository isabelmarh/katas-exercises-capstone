from .retrieval_agent import RetrievalResult


def generate_career_guidance(query: str, retrieval: RetrievalResult, memory: str) -> str:
    """Placeholder synthesis function for grounded career recommendations."""
    if retrieval.documents:
        return (
            f"Based on your documents, here is a draft answer to '{query}'. "
            "Next, replace this stub with a Pydantic AI agent."
        )
    return (
        f"I do not have enough evidence yet to answer '{query}' well. "
        "Add data and retrieval first."
    )
