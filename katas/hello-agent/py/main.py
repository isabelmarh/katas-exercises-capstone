from __future__ import annotations
from typing import Any
from pydantic_evals import Case, Dataset
from pydantic_evals.evaluators import EqualsExpected
from pydantic_ai import Agent


def main(inputs: str) -> str:
    """Simple test function that handles basic math."""

    # Create an agent using Google Gemini model
    agent = Agent(
        # model='google-gla:gemini-2.5-pro'
        model='anthropic:claude-sonnet-4-5'
    )

    result = agent.run_sync(inputs)
    return result.output


# Evaluation dataset
hello_agent_dataset = Dataset[str, str, Any](
    cases=[
        Case(
            name="hello_agent",
            inputs="Simply respond with 'Hello from Agent' without any additional markup or syntax",
            expected_output="Hello from Agent",
            metadata={"difficulty": "easy"},
            evaluators=(EqualsExpected(),),
        ),
    ],
    evaluators=[],
)

if __name__ == "__main__":
    report = hello_agent_dataset.evaluate_sync(main)
    report.print()
