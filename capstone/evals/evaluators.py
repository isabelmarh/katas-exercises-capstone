from pydantic import BaseModel


class EvalSummary(BaseModel):
    name: str
    score: float
    passed: bool
    details: str


def score_actionability(response: str) -> EvalSummary:
    lowered = response.lower()
    score = 1.0 if any(token in lowered for token in {"plan", "next", "step"}) else 0.0
    return EvalSummary(
        name="actionability",
        score=score,
        passed=score >= 0.5,
        details="Checks whether the answer suggests next actions.",
    )
