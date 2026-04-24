from __future__ import annotations

from dataclasses import dataclass
from difflib import SequenceMatcher
from pathlib import Path
from typing import Callable, Any, Literal

from pydantic import BaseModel, Field, TypeAdapter
from pydantic_ai import Agent
from pydantic_evals import Case, Dataset
from pydantic_evals.evaluators import Evaluator, EvaluatorContext, EvaluatorOutput
from pydantic_evals.evaluators.evaluator import EvaluationScalar, EvaluationReason
from pydantic_evals.reporting import RenderValueConfig
from pydantic_evals.evaluators import LLMJudge

#######################################################################################################################
## Agent
#######################################################################################################################

# Predefined list of allowed professions
ALLOWED_PROFESSIONS = Literal[
    "Paper-box factory worker",
    "Member of the Give and Take Association",
    "Housewife",
    "Detective",
    "Grocer",
    "Member of Give and Take Athletic Association",
]


class Character(BaseModel):
    first_name: str = Field(description="The character's first name", min_length=3)
    last_name: str = Field(description="The character's last name", min_length=3)
    profession: ALLOWED_PROFESSIONS = Field(description="The character's profession (must be from predefined list)")
    description: str = Field(
        description="A brief description of the character, including key traits and role in the story",
        min_length=20,)
    # TODO:
    # Add more fields e.g., last_name, profession, character, description, etc.
    # consider adding validation rules to see how the agent reacts to them
    # (e.g., profession should be one of a predefined list, description should be at least 20 characters)


agent = Agent(
    model="anthropic:claude-sonnet-4-5",
    output_type=list[Character],
    instructions="""You are an expert literary analyst specializing in character extraction from short stories.

Your task is to identify and extract ALL main characters from the provided short story text. For each main character, extract the following information:

1. **First Name**: The character's given name (minimum 3 characters)
2. **Last Name**: The character's family name (minimum 3 characters, if mentioned)
3. **Profession**: The character's occupation or role in society. MUST be one of these predefined professions:
   - Paper-box factory worker
   - Member of the Give and Take Association
   - Member of Give and Take Athletic Association
   - Housewife
   - Detective
   - Grocer
4. **Description**: A detailed summary (minimum 20 characters) that captures the character's key traits, personality, motivations, and their role/significance in the story

Validation Rules:
- Description must be at least 20 characters long
- Profession must match exactly one of the predefined professions listed above
- First and last names must be at least 3 characters each

Guidelines:
- Focus on central characters who drive the narrative forward or represent key themes
- Include supporting characters who play important roles in major plot events
- For each character, ensure the description captures both personality traits and their narrative significance
- Be thorough but avoid listing every minor character mentioned in passing
- If information is not explicitly stated, infer from the character's actions and dialogue
- When mapping character professions to the predefined list, find the closest match""",
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

    def _fuzzy_match(self, expected: str, actual: str, threshold: float = 0.8) -> bool:
        """Check if two strings match with fuzzy matching above threshold."""
        ratio = SequenceMatcher(None, expected.lower(), actual.lower()).ratio()
        return ratio >= threshold

    def _extract_key_phrases(self, text: str) -> set[str]:
        """Extract important words (>3 chars) as key phrases for matching."""
        # Split into words and filter out short words and common words
        words = text.lower().split()
        key_phrases = {
            word.strip(',.!?;:').lower() 
            for word in words 
            if len(word.strip(',.!?;:')) > 3
        }
        return key_phrases

    def _check_key_phrases_match(self, expected: str, actual: str, min_match_ratio: float = 0.5, phrase_similarity_threshold: float = 0.75) -> bool:
        """Check if at least min_match_ratio of key phrases from expected appear in actual.
        
        Uses fuzzy matching to handle variations (e.g., "escort" matches "escorting").
        """
        expected_phrases = self._extract_key_phrases(expected)
        actual_phrases = self._extract_key_phrases(actual)
        
        if not expected_phrases:
            return True
        
        # Check how many expected phrases find a match in actual phrases
        matches = 0
        for expected_phrase in expected_phrases:
            # Try exact match first
            if expected_phrase in actual_phrases:
                matches += 1
            else:
                # Try fuzzy match with actual phrases
                for actual_phrase in actual_phrases:
                    similarity = SequenceMatcher(None, expected_phrase, actual_phrase).ratio()
                    if similarity >= phrase_similarity_threshold:
                        matches += 1
                        break
        
        match_ratio = matches / len(expected_phrases)
        return match_ratio >= min_match_ratio

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

        ## check last name
        if self.last_name is not None:
            reasons["last_name"] = character.last_name == self.last_name
        else:
            reasons["last_name"] = True

        ## check profession using fuzzy matching
        if self.profession is not None:
            reasons["profession"] = self._fuzzy_match(self.profession, character.profession)
        else:
            reasons["profession"] = True
            
        ## check description using key phrase matching
        if self.description is not None and self.description != "...":
            # Match if at least 50% of key phrases from expected appear in actual
            match = self._check_key_phrases_match(self.description, character.description, min_match_ratio=0.4)
            reasons["description"] = match
        else:
            reasons["description"] = True
    
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
