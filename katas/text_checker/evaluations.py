from __future__ import annotations

from dataclasses import dataclass
from functools import cached_property
from typing import Annotated, Any

import yaml
from pydantic import Field
from pydantic_ai import Agent, PromptedOutput
from pydantic_ai.builtin_tools import UrlContextTool
from pydantic_evals import Case, Dataset
from pydantic_evals.evaluators import EvaluationReason, Evaluator, EvaluatorContext
from typing_extensions import override

from katas.text_checker.agent import Ring


@dataclass
class CorrectRingEval(Evaluator):
    """
    Evaluator that checks if the assessment's rating matches the expected rating.

    Returns a score of 1.0 on a match, 0.0 on a wrongly detected hold, 0.5 otherwise
    """

    expected_rating: Ring

    @override
    async def evaluate(
        self, ctx: EvaluatorContext[str, dict[str, Any]]
    ) -> EvaluationReason:
        if "ring" not in ctx.output:
            return EvaluationReason(value=-1, reason="No ring classification given ")

        if ctx.output["ring"] == self.expected_rating:
            score = 1.0
        elif ctx.output["ring"] == "Hold" or self.expected_rating == "Hold":
            score = 0.1
        else:
            score = 0.5

        return EvaluationReason(
            value=score, reason=f"{ctx.output['ring']} == {self.expected_rating}"
        )


@dataclass
class NumberFactsEval(Evaluator):
    """
    Evaluator that checks that $number_facts have been extracted.
    """

    number_facts: int

    @override
    async def evaluate(
        self, ctx: EvaluatorContext[str, dict[str, Any]]
    ) -> EvaluationReason:
        if "claims" not in ctx.output:
            return EvaluationReason(value=-1, reason="No claims provided")

        score = min(len(ctx.output["claims"]) / self.number_facts, 1)
        return EvaluationReason(
            value=score, reason=f"{len(ctx.output['claims'])}/{self.number_facts}"
        )


@dataclass
class SourceCredibility:
    score: Annotated[float, Field(ge=0.0, le=1.0, description="score between 0 and 1")]
    reason: Annotated[str, Field(description="short text explaining the score")]


@dataclass
class SourceCredibilityEvals(Evaluator):
    """Evaluates the credibility of all provided sources in the fact check (uses an LLM)"""

    @override
    async def evaluate(
        self, ctx: EvaluatorContext[str, dict[str, Any]]
    ) -> EvaluationReason:
        if "claims" not in ctx.output:
            return EvaluationReason(value=-1, reason="No claims provided")

        sources: list[str] = []
        for claim in ctx.output["claims"]:
            sources += [str(s) for s in claim.get("sources", None)]

        if not sources:
            return EvaluationReason(value=0, reason="No sources on claims provided")
        res = await self.agent.run(", ".join(sources))
        output = res.output
        return EvaluationReason(value=output.score, reason=output.reason)

    @cached_property
    def agent(self) -> Agent[None, SourceCredibility]:
        return Agent(
            model="google-gla:gemini-2.5-pro",
            output_type=PromptedOutput(SourceCredibility),
            builtin_tools=[UrlContextTool()],
            instructions="""
            You are a research assistant. Assess the quality of the provided sources.
            """,
        )


def load_evaluation(yaml_path: str) -> Dataset[str, dict[str, Any], Any]:
    with open(yaml_path, "r") as f:
        data = yaml.safe_load(f)

    cases: list[Case] = []
    for item in data.get("blips", []):
        cases.append(
            Case(
                name=item["name"],
                inputs=item["description"],
                expected_output=item["rating"],
                metadata={},
                evaluators=(CorrectRingEval(expected_rating=item["rating"]),),
            )
        )

    return Dataset[str, dict[str, Any], Any](
        cases=cases,
        evaluators=[NumberFactsEval(number_facts=3), SourceCredibilityEvals()],
    )
