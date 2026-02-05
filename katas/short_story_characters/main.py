from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Any

from pydantic import BaseModel, Field, TypeAdapter
from pydantic_ai import Agent
from pydantic_evals import Case, Dataset
from pydantic_evals.evaluators import Evaluator, EvaluatorContext, EvaluatorOutput
from pydantic_evals.evaluators.evaluator import EvaluationScalar, EvaluationReason
from pydantic_evals.reporting import RenderValueConfig

#######################################################################################################################
## Agent
#######################################################################################################################


class Character(BaseModel):
    first_name: str = Field(description="The character's first name", min_length=3)
    # TODO:
    # Add more fields e.g., last_name, profession, character, description, etc.
    # consider adding validation rules to see how the agent reacts to them
    # (e.g., profession should be one of a predefined list, description should be at least 20 characters)


agent = Agent(
    model="google-gla:gemini-2.5-pro",
    output_type=list[Character],
    instructions="""extract main characters""",
)

#######################################################################################################################
## Evaluations
#######################################################################################################################


@dataclass
class ContainsCharacter(Evaluator[str, list[Character]]):
    first_name: str
    last_name: str | None
    profession: str | None
    description: str | None

    def evaluate(self, ctx: EvaluatorContext[str, list[Character]]) -> EvaluatorOutput:
        reasons: dict[str, EvaluationScalar | EvaluationReason] = {}

        extracted_characters = ctx.output
        ## find character by first name
        character = next(
            (c for c in extracted_characters if c.first_name == self.first_name), None
        )

        if character is None:
            raise ValueError(
                f"Character with first name '{self.first_name}' not found in the output."
            )

        reasons["first_name"] = True

        ## TODO:
        ## Add more detailed checks for last name, profession, description, etc.
        ## Exact match might be too strict, consider using fuzzy matching
        ## or checking for key phrases in the description instead of an exact match.
        ## Consider changing the input to the evaluation to include this
        reasons["last_name"] = False
        reasons["profession"] = False
        reasons["description"] = False

        return self._prefix_reasons_with_evaluator_name(reasons)

    def _prefix_reasons_with_evaluator_name(
        self, reasons: dict[str, EvaluationScalar | EvaluationReason]
    ) -> dict[str, EvaluationScalar | EvaluationReason]:
        """prefix reason keys with the evaluation name to avoid key collisions
        in the report when multiple evaluations are used"""
        return {f"{self.first_name}_{key}": value for key, value in reasons.items()}

    def get_default_evaluation_name(self) -> str:
        # This will be used as the name of the evaluation in the report
        return f"{self.first_name}_check"


datacontract_dataset = Dataset[str, list[Character]](
    cases=[
        Case(
            name="The Coming-Out of Maggie",
            inputs=(
                Path(__file__).parent / "short_stories" / "the_coming_out_of_maggie.txt"
            ).read_text(),
            expected_output=None,
            evaluators=(
                ContainsCharacter(
                    first_name="Maggie",
                    last_name="Toole",
                    profession="Paper-box factory worker",
                    description="Plain and socially overlooked, she longs for a romantic escort",
                ),
                ContainsCharacter(
                    first_name="Anna",
                    last_name="McCarty",
                    profession="Paper-box factory worker",
                    description="...",
                ),
                ContainsCharacter(
                    first_name="Jimmy",
                    last_name="Burns",
                    profession="Member of the Give and Take Association",
                    description="Anna McCarty’s boyfriend; he is the standard against which Maggie’s new escort is initially compared.",
                ),
            ),
        ),
        Case(
            name="Lamb to the Slaughter",
            inputs=(
                Path(__file__).parent / "short_stories" / "lamb_to_the_slaughter.txt"
            ).read_text(),
            expected_output=None,
            evaluators=(
                ContainsCharacter(
                    first_name="Mary",
                    last_name="Maloney",
                    profession="Housewife",
                    description="devoted and pregnant housewife who turns into a calculating murderer,",
                ),
                ContainsCharacter(
                    first_name="Patrick",
                    last_name="Maloney",
                    profession="Detective",
                    description="tired senior police officer who abruptly decides to leave his wife",
                ),
                ContainsCharacter(
                    first_name="Sam",
                    last_name=None,
                    profession="Grocer",
                    description="kind and unsuspecting local grocer who provides Mary's alibi",
                ),
                ContainsCharacter(
                    first_name="Jack",
                    last_name="Noonan",
                    profession="Detective",
                    description="police sergeant who unwittingly consumes the murder weapon.",
                ),
            ),
        ),
    ]
)


def display_characters_as_json(characters: list[Character]) -> str:
    return TypeAdapter(list[Character]).dump_json(characters, indent=2).decode()


def run_evals() -> None:
    run_agent: Callable[[str], Any] = lambda s: agent.run_sync(s).output
    report = datacontract_dataset.evaluate_sync(run_agent)
    report.print(
        include_input=False,  # short story is quite long
        include_output=True,
        include_reasons=True,
        output_config=RenderValueConfig(value_formatter=display_characters_as_json),
    )


if __name__ == "__main__":
    run_evals()
