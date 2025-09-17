from __future__ import annotations
from typing import Any
from pydantic_evals import Case, Dataset
from pydantic_evals.evaluators import EqualsExpected


def main(inputs: str) -> str:
    """Simple test function that handles basic math."""
    if "2 + 2" in inputs:
        return "4"
    return f"I don't know how to answer: {inputs}"


# Evaluation dataset
dumb_example_dataset = Dataset[str, str, Any](
    cases=[
        Case(
            name="simple_test",
            inputs="What is 2 + 2?",
            expected_output="4",
            metadata={"difficulty": "easy"},
            evaluators=(EqualsExpected(),),
        ),
    ],
    evaluators=[],
)


if __name__ == "__main__":
    report = dumb_example_dataset.evaluate_sync(main)
    print(report)
