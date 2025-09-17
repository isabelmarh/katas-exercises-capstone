from __future__ import annotations
from typing import Any
from pydantic_evals import Case, Dataset
from pydantic_evals.evaluators import EqualsExpected


def main(text: str) -> str:
    """
    Punctuation and Capitalization Agent

    This function should add proper punctuation and capitalization to text while
    preserving all original words exactly as they appear.

    Rules:
    - Insert punctuation marks: comma (,), period (.), and question mark (?)
    - Correct capitalization:
      - Capitalize the first word of each sentence
      - Capitalize acronyms (e.g., CIA, NASA)
      - Capitalize proper nouns (e.g., Berlin, June)

    Critical constraints:
    - PRESERVE every single word from the original text (no deletions, no rewording)
    - PRESERVE spelling exactly, even if incorrect
    - PRESERVE word order (do not reorder)
    - ONLY INSERT punctuation and capitalization corrections
    - DO NOT fix typos, grammar, or semantics beyond punctuation/capitalization
    - DO NOT add or remove words
    - DO NOT split or merge words
    - DO NOT add any punctuation other than , . ?

    Args:
        text: The input text that needs punctuation and capitalization

    Returns:
        The text with proper punctuation and capitalization added
    """
    # TODO: Implement punctuation and capitalization agent

    raise NotImplementedError("Punctuation and capitalization agent not implemented")


# Evaluation dataset
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
            expected_output="When I went to the store, it was closed so I came back home.",
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
            name="acronym_caps",
            inputs="cia operative said go now do you agree",
            expected_output="CIA operative said go now. Do you agree?",
            metadata={"difficulty": "medium"},
            evaluators=(EqualsExpected(),),
        ),
        Case(
            name="long_run_on_to_sentences",
            inputs="we met in berlin in june we walked the river we talked about work and travel is that okay with you",
            expected_output="We met in Berlin in June. We walked the river. We talked about work and travel. Is that okay with you?",
            metadata={"difficulty": "hard"},
            evaluators=(EqualsExpected(),),
        ),
    ],
    evaluators=[],
)


if __name__ == "__main__":
    report = punctuation_dataset.evaluate_sync(main)
    print(report)
