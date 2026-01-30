from pydantic_evals import BaseEval, EvalResult
from opentelemetry import trace

tracer = trace.get_tracer(__name__)


class RetrievalAccuracyEval(BaseEval):
    """Evaluate retrieval precision using Pydantic Evals."""

    def evaluate(
        self, retrieved_docs: list[str], relevant_docs: list[str]
    ) -> EvalResult:
        if not retrieved_docs:
            return EvalResult(
                score=0.0, passed=False, metadata={"reason": "No documents retrieved"}
            )

        relevant_count = sum(
            1 for doc in retrieved_docs if any(rel in doc for rel in relevant_docs)
        )
        precision = relevant_count / len(retrieved_docs)

        return EvalResult(
            score=precision,
            passed=precision >= 0.7,
            metadata={
                "precision": precision,
                "retrieved_count": len(retrieved_docs),
                "relevant_found": relevant_count,
            },
        )


class ResponseQualityEval(BaseEval):
    """Evaluate response quality using Pydantic Evals."""

    def evaluate(self, query: str, response: str, context: list[str]) -> EvalResult:
        score = 0.0
        reasons = []

        if len(response) < 50:
            reasons.append("Response too short")
        else:
            score += 0.3
            reasons.append("Adequate length")

        context_used = any(
            snippet in response for doc in context for snippet in doc.split()[:10]
        )
        if context_used:
            score += 0.4
            reasons.append("Uses retrieved context")
        else:
            reasons.append("Doesn't reference context")

        if query.lower() in response.lower() or any(
            word in response.lower() for word in query.lower().split()
        ):
            score += 0.3
            reasons.append("Addresses query")
        else:
            reasons.append("Doesn't clearly address query")

        return EvalResult(
            score=score,
            passed=score >= 0.6,
            metadata={
                "reasoning": " | ".join(reasons),
                "response_length": len(response),
            },
        )


class RAGEvaluator:
    """Main evaluator using Pydantic Evals framework."""

    def __init__(self):
        self.retrieval_eval = RetrievalAccuracyEval()
        self.quality_eval = ResponseQualityEval()

    @tracer.start_as_current_span("evaluate_system")
    def evaluate_system(self, test_cases: list[dict]) -> dict:
        results = {
            "retrieval_precision": [],
            "response_quality": [],
            "overall_pass_rate": 0.0,
        }

        passed_count = 0

        for case in test_cases:
            retrieval_result = self.retrieval_eval.evaluate(
                case["retrieved"], case["relevant"]
            )
            results["retrieval_precision"].append(retrieval_result.score)

            quality_result = self.quality_eval.evaluate(
                case["query"], case["response"], case["retrieved"]
            )
            results["response_quality"].append(quality_result.score)

            if retrieval_result.passed and quality_result.passed:
                passed_count += 1

        results["overall_pass_rate"] = (
            passed_count / len(test_cases) if test_cases else 0.0
        )
        results["avg_retrieval_precision"] = (
            sum(results["retrieval_precision"]) / len(results["retrieval_precision"])
            if results["retrieval_precision"]
            else 0.0
        )
        results["avg_quality_score"] = (
            sum(results["response_quality"]) / len(results["response_quality"])
            if results["response_quality"]
            else 0.0
        )

        return results


def run_evaluation_suite():
    """Run comprehensive evaluation using Pydantic Evals."""
    evaluator = RAGEvaluator()

    test_cases = [
        {
            "query": "How do I create an agent?",
            "retrieved": [
                "Agent creation guide: Use Agent class from pydantic_ai",
                "API reference for agents",
            ],
            "response": "To create an agent, use the Agent class from pydantic_ai. Import it and instantiate with your model string.",
            "relevant": ["Agent creation", "pydantic_ai"],
        },
        {
            "query": "What is RAG?",
            "retrieved": [
                "RAG stands for Retrieval Augmented Generation",
                "RAG combines search with LLMs",
            ],
            "response": "RAG (Retrieval Augmented Generation) combines vector search with language models to provide context-aware responses.",
            "relevant": ["RAG", "Retrieval"],
        },
        {
            "query": "How to add memory?",
            "retrieved": [
                "Memory can be added using the deps system",
                "Store conversation history",
            ],
            "response": "Add memory by using the deps system to pass conversation history to your agents.",
            "relevant": ["memory", "deps"],
        },
    ]

    results = evaluator.evaluate_system(test_cases)

    print("\n=== Evaluation Results (Pydantic Evals) ===")
    print(f"Average Retrieval Precision: {results['avg_retrieval_precision']:.2f}")
    print(f"Average Response Quality: {results['avg_quality_score']:.2f}")
    print(f"Overall Pass Rate: {results['overall_pass_rate']:.2%}")

    return results


if __name__ == "__main__":
    run_evaluation_suite()
