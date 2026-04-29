from __future__ import annotations

from pydantic_ai import Agent

from .model_factory import build_model, offline_text_response


baseline_agent = Agent(
    build_model("baseline"),
    output_type=str,
    instructions=(
        "You are a generic career chatbot. Give concise advice without retrieval, memory, "
        "or citing any local documents."
    ),
    defer_model_check=True,
)


def generate_baseline_response(query: str) -> str:
    try:
        return baseline_agent.run_sync(query).output
    except Exception:
        return offline_text_response("baseline", query)
