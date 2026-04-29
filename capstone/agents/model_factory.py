from __future__ import annotations

import json
import os
import re
from collections.abc import Sequence
from typing import Any

from pydantic_ai.messages import ModelMessage, ModelResponse, TextPart
from pydantic_ai.models.function import FunctionModel

try:
    from ..env import load_local_env
except ImportError:
    from env import load_local_env


load_local_env()


def has_live_model() -> bool:
    return any(
        bool(os.getenv(name, "").strip())
        for name in ("ANTHROPIC_API_KEY", "GOOGLE_API_KEY", "GEMINI_API_KEY")
    )


def live_model_name() -> str:
    if os.getenv("ANTHROPIC_API_KEY", "").strip():
        return "anthropic:claude-sonnet-4-5"
    if os.getenv("GOOGLE_API_KEY", "").strip() or os.getenv("GEMINI_API_KEY", "").strip():
        return "google-gla:gemini-2.5-pro"
    raise RuntimeError("No live model API key is configured.")


def active_model_label() -> str:
    if has_live_model():
        return live_model_name()
    return "offline-function-model"


def fallback_model_label(agent_kind: str) -> str:
    return f"offline-{agent_kind}"


def build_model(agent_kind: str):
    if has_live_model():
        return live_model_name()
    return FunctionModel(
        lambda messages, info: ModelResponse(
            parts=[TextPart(content=_offline_response(agent_kind, _extract_prompt(messages)))]
        ),
        model_name=f"offline-{agent_kind}",
    )


def offline_text_response(agent_kind: str, prompt: str) -> str:
    """Expose the deterministic offline response for graceful degradation."""
    return _offline_response(agent_kind, prompt)


def _extract_prompt(messages: Sequence[ModelMessage]) -> str:
    parts: list[str] = []
    for message in messages:
        for part in getattr(message, "parts", []):
            content = getattr(part, "content", None)
            if isinstance(content, str):
                parts.append(content)
    return "\n".join(parts)


def _offline_response(agent_kind: str, prompt: str) -> str:
    if agent_kind == "router":
        return _offline_router_response(prompt)
    if agent_kind == "preferences":
        return _offline_preferences_response(prompt)
    if agent_kind == "baseline":
        return _offline_baseline_response(prompt)
    if agent_kind == "coach":
        return _offline_coach_response(prompt)
    if agent_kind == "trajectory":
        return _offline_trajectory_response(prompt)
    return ""


def _offline_router_response(prompt: str) -> str:
    lowered = prompt.lower()
    route = "direct"
    confidence = 0.55
    reasoning = "generic query"

    if any(
        token in lowered
        for token in {"trajectory", "roadmap", "skill gap", "missing skills", "compare roles", "compare career paths"}
    ):
        route = "planning"
        confidence = 0.88
        reasoning = "query asks for structured trajectory planning"
    elif any(token in lowered for token in {"remember", "preference", "prefer", "remote", "salary"}):
        route = "memory"
        confidence = 0.82
        reasoning = "user preference or memory lookup"
    elif any(
        token in lowered
        for token in {"why", "what role", "skills", "career", "job", "path", "backend", "platform", "ai"}
    ):
        route = "retrieval"
        confidence = 0.9
        reasoning = "query needs grounded career evidence"

    return json.dumps(
        {"route": route, "confidence": confidence, "reasoning": reasoning},
        ensure_ascii=True,
    )


def _offline_preferences_response(prompt: str) -> str:
    lowered = prompt.lower()
    preferences: dict[str, str] = {}

    work_mode = re.search(r"\b(remote|hybrid|onsite)\b", lowered)
    role_interest = re.search(
        r"\b(backend|frontend|platform|ai|ml|data|staff|leadership|management)\b",
        lowered,
    )
    company_preference = re.search(r"\b(startup|enterprise)\b", lowered)

    if work_mode:
        preferences["work_mode"] = work_mode.group(1)
    if role_interest:
        preferences["role_interest"] = role_interest.group(1)
    if company_preference:
        preferences["company_preference"] = company_preference.group(1)

    return json.dumps(preferences, ensure_ascii=True)


def _offline_baseline_response(prompt: str) -> str:
    query = prompt.strip().splitlines()[-1]
    return (
        f"Generic advice for '{query}': choose one role direction, improve one high-leverage skill, "
        "tailor your resume, and apply consistently for the next month."
    )


def _offline_coach_response(prompt: str) -> str:
    payload = json.loads(prompt)
    query = str(payload["query"])
    memory = str(payload["memory"])
    evidence_items = payload["evidence"]

    if not evidence_items:
        return (
            "I do not have enough relevant evidence yet. Add more notes, job descriptions, "
            "or reflections under capstone/data/raw and run ingestion again."
        )

    sources = [item["source"] for item in evidence_items[:3]]
    docs = [item["document"] for item in evidence_items[:3]]
    evidence = "\n".join(
        f"- Evidence from {source}: {document[:180].strip()}..."
        for source, document in zip(sources, docs)
    )

    focus_area = "backend and platform-oriented growth"
    lowered_query = query.lower()
    if "ai" in lowered_query or any("ai" in doc.lower() for doc in docs):
        focus_area = "an AI-leaning engineering path with strong backend fundamentals"
    elif any("platform" in doc.lower() for doc in docs):
        focus_area = "platform engineering with reliability and infrastructure depth"

    memory_line = memory if memory.strip() else "- No saved preferences yet."
    return (
        f"Recommendation: prioritize {focus_area}.\n\n"
        f"Why this fits:\n{evidence}\n\n"
        f"Stored preferences and context:\n{memory_line}\n\n"
        "Suggested next steps:\n"
        "- Pick one target role family and compare your resume against 3 saved job descriptions.\n"
        "- Build one portfolio project that demonstrates the missing skills that show up repeatedly.\n"
        "- Spend the next 2 weeks writing short reflection notes after each learning session so future recommendations improve.\n\n"
        f"Retrieved from: {', '.join(sources)}"
    )


def _offline_trajectory_response(prompt: str) -> str:
    payload = json.loads(prompt)
    query = str(payload["query"])
    role = "AI Engineer" if "ai" in query.lower() else "Platform Engineer"
    return json.dumps(
        {
            "target_role": role,
            "strengths": [
                "backend implementation",
                "systems thinking",
                "evaluation-driven reflection",
            ],
            "skill_gaps": [
                "deeper production-grade infrastructure evidence",
                "clearer portfolio proof aligned to the target role",
            ],
            "recommended_projects": [
                "Build a portfolio project that combines backend APIs with observability.",
                "Write a role-targeted case study from one existing project.",
            ],
            "next_steps": [
                "Compare your resume against three target job descriptions.",
                "Build one project that demonstrates the missing skills.",
                "Review progress weekly and update your learning notes.",
            ],
            "confidence": 0.78,
            "rationale": "Your documents point toward backend strength with adjacent growth into platform or AI-oriented work.",
        },
        ensure_ascii=True,
    )
