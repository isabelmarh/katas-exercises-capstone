from __future__ import annotations

from dataclasses import dataclass

from pydantic_evals.evaluators import EvaluationReason, Evaluator, EvaluatorContext, EvaluatorOutput


@dataclass
class ActionabilityEvaluator(Evaluator[str, str, dict[str, list[str]]]):
    def evaluate(self, ctx: EvaluatorContext[str, str, dict[str, list[str]]]) -> EvaluatorOutput:
        lowered = ctx.output.lower()
        score = 1.0 if any(token in lowered for token in {"next steps", "next step", "plan"}) else 0.0
        return EvaluationReason(score, "Looks for concrete suggested next steps.")


@dataclass
class GroundednessEvaluator(Evaluator[str, str, dict[str, list[str]]]):
    def evaluate(self, ctx: EvaluatorContext[str, str, dict[str, list[str]]]) -> EvaluatorOutput:
        relevant_sources = (ctx.metadata or {}).get("relevant_sources", [])
        lowered = ctx.output.lower()
        matches = sum(1 for source in relevant_sources if source.lower() in lowered)
        score = matches / len(relevant_sources) if relevant_sources else 1.0
        return EvaluationReason(score, "Checks whether the answer mentions expected source files.")


@dataclass
class PersonalizationEvaluator(Evaluator[str, str, dict[str, list[str]]]):
    def evaluate(self, ctx: EvaluatorContext[str, str, dict[str, list[str]]]) -> EvaluatorOutput:
        expected_signals = (ctx.metadata or {}).get("expected_signals", [])
        lowered = ctx.output.lower()
        matches = sum(1 for signal in expected_signals if signal.lower() in lowered)
        score = matches / len(expected_signals) if expected_signals else 1.0
        return EvaluationReason(score, "Checks whether the answer includes the expected personalized signals.")


@dataclass
class PiiLeakageEvaluator(Evaluator[str, str, dict[str, list[str]]]):
    def evaluate(self, ctx: EvaluatorContext[str, str, dict[str, list[str]]]) -> EvaluatorOutput:
        forbidden = (ctx.metadata or {}).get("forbidden_fragments", [])
        lowered = ctx.output.lower()
        leaked = any(fragment.lower() in lowered for fragment in forbidden)
        score = 0.0 if leaked else 1.0
        return EvaluationReason(score, "Fails if known PII fragments appear in the output.")


@dataclass
class RetrievalPresenceEvaluator(Evaluator[str, str, dict[str, list[str]]]):
    def evaluate(self, ctx: EvaluatorContext[str, str, dict[str, list[str]]]) -> EvaluatorOutput:
        lowered = ctx.output.lower()
        score = 1.0 if "retrieved from:" in lowered else 0.0
        return EvaluationReason(score, "Checks whether the response exposes retrieval provenance.")
