from __future__ import annotations

from dataclasses import dataclass
from functools import cached_property
from typing import Annotated

from pydantic import Field
from pydantic_ai import Agent, PromptedOutput
from pydantic_ai.builtin_tools import UrlContextTool
from pydantic_evals.evaluators import EvaluationReason, Evaluator, EvaluatorContext
from typing_extensions import override

from katas.text_checker.models import Assessment, Rating


@dataclass
class CorrectAssessmentEval(Evaluator):
    """
    Evaluator that checks if the assessment's rating matches the expected rating.

    Returns a score of 1.0 on a match, 0.0 on a wrongly detected hold, 0.5 otherwise
    """

    expected_rating: Rating

    @override
    async def evaluate(
        self, ctx: EvaluatorContext[str, Assessment]
    ) -> EvaluationReason:
        if ctx.output.rating == self.expected_rating:
            score = 1.0
        elif ctx.output.rating == "Hold" or self.expected_rating == "Hold":
            score = 0.0
        else:
            score = 0.5

        return EvaluationReason(
            value=score, reason=f"{ctx.output.rating} == {self.expected_rating}"
        )


@dataclass
class AmountFactsEval(Evaluator):
    """
    Evaluator that checks that $number_facts have been extracted.
    """

    number_facts: int

    @override
    async def evaluate(
        self, ctx: EvaluatorContext[str, Assessment]
    ) -> EvaluationReason:
        score = min(len(ctx.output.claims) / self.number_facts, 1)
        return EvaluationReason(
            value=score, reason=f"{len(ctx.output.claims)}/{self.number_facts}"
        )


@dataclass
class SourceCredability:
    score: Annotated[float, Field(ge=0.0, le=1.0, description="score between 0 and 1")]
    reason: Annotated[str, Field(description="short text explaining the score")]


@dataclass
class SourceCredabilityEvals(Evaluator):
    """Evaluates the credability of all provided sources in the fact check (uses an LLM)"""

    @override
    async def evaluate(
        self, ctx: EvaluatorContext[str, Assessment]
    ) -> EvaluationReason:
        sources: list[str] = []
        for claim in ctx.output.claims:
            sources += [str(s) for s in claim.sources]
        res = await self.agent.run(", ".join(sources))
        output = res.output
        return EvaluationReason(value=output.score, reason=output.reason)

    @cached_property
    def agent(self) -> Agent[None, SourceCredability]:
        return Agent(
            model="google-gla:gemini-2.5-pro",
            output_type=PromptedOutput(SourceCredability),
            builtin_tools=[UrlContextTool()],
            instructions="""
            You are a research assistant. Assess the quality of the provided sources.
            """,
        )
