from __future__ import annotations

import json

from pydantic import BaseModel
from pydantic_ai import Agent

from .model_factory import build_model, offline_text_response


class QueryRoute(BaseModel):
    route: str
    confidence: float
    reasoning: str


router_agent = Agent(
    build_model("router"),
    output_type=str,
    instructions=(
        "Classify the user's career query. Return minified JSON with keys route, confidence, reasoning. "
        "Allowed routes: retrieval, memory, direct, planning."
    ),
    defer_model_check=True,
)


def route_query(query: str) -> QueryRoute:
    try:
        result = router_agent.run_sync(query)
        raw_output = result.output
    except Exception:
        raw_output = offline_text_response("router", query)

    try:
        parsed = json.loads(raw_output)
        return QueryRoute.model_validate(parsed)
    except Exception:
        return QueryRoute(route="direct", confidence=0.5, reasoning="fallback parsing path")
