from __future__ import annotations

import json

from pydantic import BaseModel
from pydantic_ai import Agent

from .model_factory import build_model, offline_text_response


class PreferenceExtraction(BaseModel):
    work_mode: str | None = None
    role_interest: str | None = None
    company_preference: str | None = None


preference_agent = Agent(
    build_model("preferences"),
    output_type=str,
    instructions=(
        "Extract only stable career preferences from the user's message. "
        "Return minified JSON with optional keys: work_mode, role_interest, company_preference. "
        "If none are present, return {}."
    ),
    defer_model_check=True,
)


def extract_preferences_from_query(query: str) -> dict[str, str]:
    try:
        result = preference_agent.run_sync(query)
        raw_output = result.output
    except Exception:
        raw_output = offline_text_response("preferences", query)

    try:
        parsed = json.loads(raw_output)
        return PreferenceExtraction.model_validate(parsed).model_dump(exclude_none=True)
    except Exception:
        return {}
