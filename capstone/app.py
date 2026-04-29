from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

try:
    from .agents.baseline_agent import generate_baseline_response
    from .agents.career_coach_agent import generate_career_guidance
    from .agents.memory_agent import get_memory_store
    from .agents.preference_agent import extract_preferences_from_query
    from .agents.retrieval_agent import RetrievalResult, retrieve_documents
    from .agents.router_agent import route_query
    from .agents.trajectory_agent import generate_trajectory_plan
    from .guardrails import sanitize_model_output, sanitize_user_input
    from .memory.summarizer import format_preferences, summarize_episode, summarize_messages
    from .rag.ingest import ingest_directory
    from .telemetry import span
except ImportError:
    from agents.baseline_agent import generate_baseline_response
    from agents.career_coach_agent import generate_career_guidance
    from agents.memory_agent import get_memory_store
    from agents.preference_agent import extract_preferences_from_query
    from agents.retrieval_agent import RetrievalResult, retrieve_documents
    from agents.router_agent import route_query
    from agents.trajectory_agent import generate_trajectory_plan
    from guardrails import sanitize_model_output, sanitize_user_input
    from memory.summarizer import format_preferences, summarize_episode, summarize_messages
    from rag.ingest import ingest_directory
    from telemetry import span


@dataclass
class QueryExecution:
    """Structured record of one end-to-end query execution."""

    query: str
    sanitized_query: str
    route: str
    route_reasoning: str
    used_memory: bool
    retrieved_sources: list[str]
    response: str
    pii_found_in_input: bool
    pii_found_in_output: bool
    prompt_injection_detected: bool


def _ensure_index_exists() -> None:
    root = Path(__file__).resolve().parent
    data_dir = root / "data" / "raw"
    index_path = root / "storage" / "career_index.json"
    if index_path.exists():
        return
    ingest_directory(data_dir, index_path)


def _baseline_response(query: str) -> str:
    return generate_baseline_response(query)


def run_query(query: str, use_memory: bool = True, top_k: int = 3) -> str:
    """Run the local MVP end-to-end for one user query."""
    execution = run_query_with_metadata(query, use_memory=use_memory, top_k=top_k)
    return execution.response


def run_query_with_metadata(
    query: str, use_memory: bool = True, top_k: int = 3
) -> QueryExecution:
    """Run the local MVP and return orchestration metadata for debugging and evals."""
    _ensure_index_exists()
    input_guardrail = sanitize_user_input(query)
    sanitized_query = input_guardrail.sanitized_text
    store = get_memory_store()

    with span(
        "save_user_message",
        pii_found=input_guardrail.pii_found,
        prompt_injection_detected=input_guardrail.prompt_injection_detected,
    ):
        store.save_message("user", sanitized_query)

    with span("route_query"):
        route = route_query(sanitized_query)

    with span("update_preferences"):
        for key, value in extract_preferences_from_query(sanitized_query).items():
            store.save_preference(key, value)

    recent_messages = store.get_recent_messages(limit=6)
    previous_messages = recent_messages[:-1]
    preferences = store.get_preferences() if use_memory else {}
    memory_summary = summarize_messages(previous_messages) if use_memory else ""
    preference_summary = format_preferences(preferences)
    combined_memory = "\n".join(
        part for part in [preference_summary, memory_summary] if part
    )

    retrieval = RetrievalResult(
        documents=[],
        scores=[],
        query=sanitized_query,
        sources=[],
        categories=[],
    )
    if route.route in {"retrieval", "direct", "memory"}:
        with span("retrieve_documents", top_k=top_k):
            retrieval = retrieve_documents(sanitized_query, top_k=top_k)

    with span("generate_response"):
        if route.route == "planning":
            trajectory = generate_trajectory_plan(sanitized_query)
            raw_response = (
                f"Trajectory target: {trajectory.target_role}\n\n"
                f"Rationale: {trajectory.rationale}\n\n"
                "Strengths:\n"
                + "\n".join(f"- {item}" for item in trajectory.strengths)
                + "\n\nSkill gaps:\n"
                + "\n".join(f"- {item}" for item in trajectory.skill_gaps)
                + "\n\nRecommended projects:\n"
                + "\n".join(f"- {item}" for item in trajectory.recommended_projects)
                + "\n\nNext steps:\n"
                + "\n".join(f"- {item}" for item in trajectory.next_steps)
                + f"\n\nConfidence: {trajectory.confidence:.2f}"
            )
        elif route.route == "direct" and not retrieval.documents:
            raw_response = _baseline_response(sanitized_query)
        else:
            raw_response = generate_career_guidance(
                sanitized_query, retrieval, combined_memory
            )

    output_guardrail = sanitize_model_output(raw_response)
    response = output_guardrail.sanitized_text

    with span("save_assistant_message", pii_found=output_guardrail.pii_found):
        store.save_message("assistant", response)
        episode_summary, tags, relevance_score = summarize_episode(
            sanitized_query, response
        )
        store.save_episode(episode_summary, tags, relevance_score=relevance_score)

    return QueryExecution(
        query=query,
        sanitized_query=sanitized_query,
        route=route.route,
        route_reasoning=route.reasoning,
        used_memory=use_memory,
        retrieved_sources=retrieval.sources,
        response=response,
        pii_found_in_input=input_guardrail.pii_found,
        pii_found_in_output=output_guardrail.pii_found,
        prompt_injection_detected=input_guardrail.prompt_injection_detected,
    )
