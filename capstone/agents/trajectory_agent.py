from __future__ import annotations

import json

from pydantic import BaseModel, Field
from pydantic_ai import Agent
from pydantic_ai.exceptions import ModelRetry

from .memory_agent import get_memory_store
from .model_factory import build_model, offline_text_response
from .retrieval_agent import retrieve_documents


class CareerTrajectoryPlan(BaseModel):
    target_role: str = Field(min_length=3)
    strengths: list[str] = Field(min_length=2)
    skill_gaps: list[str] = Field(min_length=2)
    recommended_projects: list[str] = Field(min_length=1)
    next_steps: list[str] = Field(min_length=3)
    confidence: float = Field(ge=0.0, le=1.0)
    rationale: str = Field(min_length=20)


trajectory_agent = Agent(
    build_model("trajectory"),
    output_type=CareerTrajectoryPlan,
    instructions=(
        "You are a structured career trajectory planner. Use your tools to inspect local evidence, "
        "semantic preferences, and episodic memory before proposing a role trajectory."
    ),
    defer_model_check=True,
)


@trajectory_agent.tool_plain
def retrieve_role_evidence(query: str) -> str:
    """Retrieve the most relevant local evidence for a role-planning query."""
    retrieval = retrieve_documents(query, top_k=4)
    return json.dumps(
        [
            {
                "source": source,
                "document": document,
                "score": score,
            }
            for source, document, score in zip(
                retrieval.sources,
                retrieval.documents,
                retrieval.scores,
            )
        ],
        ensure_ascii=True,
    )


@trajectory_agent.tool_plain
def load_semantic_preferences() -> str:
    """Load long-lived user preferences such as work mode and role direction."""
    return json.dumps(get_memory_store().get_preferences(), ensure_ascii=True)


@trajectory_agent.tool_plain
def load_episodic_memories(topic_hint: str) -> str:
    """Load recent episodic memories relevant to the current topic."""
    topic_terms = [term.strip() for term in topic_hint.lower().split() if term.strip()]
    return json.dumps(
        get_memory_store().get_relevant_episodes(topic_terms, limit=4),
        ensure_ascii=True,
    )


@trajectory_agent.output_validator
def validate_trajectory_output(output: CareerTrajectoryPlan) -> CareerTrajectoryPlan:
    if len(output.next_steps) < 3:
        raise ModelRetry("Return at least three concrete next steps.")
    if len(output.skill_gaps) < 2:
        raise ModelRetry("Return at least two meaningful skill gaps.")
    return output


def generate_trajectory_plan(query: str) -> CareerTrajectoryPlan:
    """Generate a structured career trajectory plan using Pydantic AI tools."""
    try:
        return trajectory_agent.run_sync(query).output
    except Exception:
        fallback = offline_text_response(
            "trajectory",
            json.dumps({"query": query}, ensure_ascii=True),
        )
        return CareerTrajectoryPlan.model_validate_json(fallback)
