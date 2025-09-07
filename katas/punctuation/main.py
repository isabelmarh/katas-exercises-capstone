import difflib
from typing import Final

from pydantic_ai import Agent, ModelRetry, RunContext

ALLOWED: Final[set[str]] = {",", ".", "?"}
INSTRUCTIONS = """
CRITICAL TASK: ADD PUNCTUATION AND CAPITALISATION ONLY – DO NOT MODIFY TEXT OTHERWISE

You are a punctuation-and-capitalisation processor.
Your sole function is to:
	•	Insert punctuation marks: comma (,), period (.), and question mark (?)
	•	Correct capitalisation:
	•	Capitalise the first word of each sentence.
	•	Capitalise acronyms (e.g., CIA, NASA).
	•	Capitalise proper nouns (e.g., Berlin, June).

⸻

ABSOLUTE RULES – VIOLATIONS WILL CAUSE TASK FAILURE
	1.	PRESERVE every single word from the original text (no deletions, no rewording).
	2.	PRESERVE spelling exactly, even if incorrect.
	3.	PRESERVE word order (do not reorder).
	4.	ONLY INSERT punctuation and capitalisation corrections.
	5.	DO NOT fix typos, grammar, or semantics beyond punctuation/capitalisation.
	6.	DO NOT add or remove words.
	7.	DO NOT split or merge words.
	8.	DO NOT add any punctuation other than , . ?.

⸻

INPUT PROCESSING PROTOCOL
	•	Read the input character by character.
	•	Identify where punctuation belongs.
	•	Apply capitalisation rules.
	•	Return the exact same text with ONLY punctuation and capitalisation adjusted.

⸻

FORBIDDEN ACTIONS (NEVER DO THESE)
	•	Changing any word (e.g., hostile → hostel).
	•	Correcting spelling mistakes.
	•	Adding/removing/reordering words.
	•	Adding punctuation other than , . ?.

⸻

VERIFICATION CHECKLIST

☐ Every word from input appears in output.
☐ Word count is identical.
☐ Character sequence (excluding punctuation and capitalisation) is identical.
☐ Only additions are , . ? or capitalisation.

⸻

OUTPUT FORMAT

Return ONLY the punctuated and capitalised text.
No explanations, no comments, no formatting.
"""

agent = Agent(
    model="google-gla:gemini-2.5-pro",
    instructions=INSTRUCTIONS,
)


@agent.output_validator
def guard(ctx: RunContext, value: str) -> str:
    assert isinstance(ctx.prompt, str)
    original = ctx.prompt
    edited = value

    sm = difflib.SequenceMatcher(None, original, edited, autojunk=False)
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal":
            continue
        if tag == "delete":
            deleted = original[i1:i2]
            raise ModelRetry(
                f"Illegal deletion: '{deleted}'. Only ',', '.', '?' or capitalization may be inserted."
            )
        if tag == "replace":
            orig = original[i1:i2]
            new = edited[j1:j2]
            if orig.lower() == new.lower():
                continue
            raise ModelRetry(
                f"Illegal replacement: '{orig}' → '{new}'. Only ',', '.', '?' or capitalization allowed."
            )
        if tag == "insert":
            inserted = edited[j1:j2]
            illegal = [ch for ch in inserted if ch not in ALLOWED]
            if illegal:
                raise ModelRetry(
                    f"Illegal characters inserted: '{''.join(illegal)}'. Only ',', '.', '?' allowed."
                )

    return edited


if __name__ == "__main__":
    raw = "i saw a hostile crowd at the station did you mean hostel or hostile i asked"
    res = agent.run_sync(raw)
    print(res.output)
