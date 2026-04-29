from __future__ import annotations

import json

from pydantic_ai import Agent

from .model_factory import build_model, offline_text_response
from .retrieval_agent import RetrievalResult


career_coach_agent = Agent(
    build_model("coach"),
    output_type=str,
    instructions=(
        "You are a grounded career coach. You will receive a JSON payload with query, memory, and evidence. "
        "Use only the evidence provided. Respond with: Recommendation, Why this fits, Stored preferences and context, "
        "Suggested next steps, and Retrieved from."
    ),
    defer_model_check=True,
)


def generate_career_guidance(query: str, retrieval: RetrievalResult, memory: str) -> str:
    """Generate grounded career guidance through a Pydantic AI agent."""
    payload = {
        "query": query,
        "memory": memory,
        "evidence": [
            {"source": source, "document": document, "score": score}
            for source, document, score in zip(
                retrieval.sources,
                retrieval.documents,
                retrieval.scores,
            )
        ],
    }
    prompt = json.dumps(payload, ensure_ascii=True)
    try:
        return career_coach_agent.run_sync(prompt).output
    except Exception:
        return offline_text_response("coach", prompt)
