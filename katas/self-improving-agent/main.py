from __future__ import annotations
from pathlib import Path
from typing import Any

from pydantic.main import BaseModel
from pydantic_evals import Case, Dataset
from pydantic_evals.evaluators import EqualsExpected
from pydantic_ai import Agent


def get_instructions() -> str:
    path = Path("katas/self-improving-agent/instructions.md")
    if path.exists():
        return path.read_text().strip()
    default = "Base instructions"
    _ = path.write_text(default)
    return default


def save_instructions(instructions: str) -> None:
    Path("katas/self-improving-agent/instructions.md").write_text(instructions)


async def punctuate_agent(text: str) -> str:
    agent = Agent(
        model="google-gla:gemini-2.5-pro",
        instructions=get_instructions(),
    )
    result = await agent.run(text)
    output = result.output
    assert isinstance(output, str)
    return output


class Improvement(BaseModel):
    instructions: str
    reason: str


async def improve_instructions_agent(prompt: str) -> Improvement:
    agent = Agent(
        model="google-gla:gemini-2.5-pro",
        instructions=(
            "Improve the instructions based on the feedback. "
            "Make the minimum necessary changes to fix the problem."
        ),
        output_type=Improvement,
    )
    result = await agent.run(prompt)
    return result.output


punctuation_dataset = Dataset[str, str, Any](
    cases=[
        Case(
            name="simple_sentence",
            inputs="hello world how are you today",
            expected_output="Hello, world. How are you today?",
            metadata={"difficulty": "easy"},
            evaluators=(EqualsExpected(),),
        ),
        Case(
            name="clause_commas_and_split",
            inputs="when i went to the store it was closed so i came back home",
            expected_output="When I went to the store, it was closed, so I came back home.",
            metadata={"difficulty": "medium"},
            evaluators=(EqualsExpected(),),
        ),
        Case(
            name="acronym_caps",
            inputs="cia operative said go now do you agree",
            expected_output="CIA operative said, Go now. Do you agree?",
            metadata={"difficulty": "medium"},
            evaluators=(EqualsExpected(),),
        ),
        Case(
            name="multiple_questions",
            inputs="you paid the invoice right when is the next one due",
            expected_output="You paid the invoice, right? When is the next one due?",
            metadata={"difficulty": "easy"},
            evaluators=(EqualsExpected(),),
        ),
        Case(
            name="capitalization_only_plus_period",
            inputs="this should end with a period",
            expected_output="This should end with a period.",
            metadata={"difficulty": "easy"},
            evaluators=(EqualsExpected(),),
        ),
        Case(
            name="short_ack_exchange",
            inputs="this is fine right yes of course",
            expected_output="This is fine, right? Yes, of course.",
            metadata={"difficulty": "easy"},
            evaluators=(EqualsExpected(),),
        ),
        Case(
            name="long_run_on_to_sentences",
            inputs=(
                "we met in berlin in june we walked the river we talked about work and travel "
                "is that okay with you"
            ),
            expected_output=(
                "We met in Berlin in June. We walked the river. "
                "We talked about work and travel. Is that okay with you?"
            ),
            metadata={"difficulty": "hard"},
            evaluators=(EqualsExpected(),),
        ),
    ],
)


async def main() -> None:
    report = await punctuation_dataset.evaluate(punctuate_agent)

    failures: list[str] = []
    for case in report.cases:
        if any(not result.value for result in case.assertions.values()):
            failures.append(
                f"Input: '{case.inputs}' → Expected: '{case.expected_output}' → Got: '{case.output}'"
            )

    feedback = "Failures:\n" + "\n".join(failures) if failures else "All cases passed"

    report.print(include_output=True, include_input=True, include_expected_output=True)

    current_instructions = get_instructions()
    improvement_prompt = (
        f"Current instructions:\n{current_instructions}\n\n{feedback}\n\n"
        "Analyze what the agent is doing wrong and improve the instructions "
        "to fix these specific failures."
    )

    improved = await improve_instructions_agent(improvement_prompt)
    save_instructions(improved.instructions)
    print(f"Improved! Reason: {improved.reason}")


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
