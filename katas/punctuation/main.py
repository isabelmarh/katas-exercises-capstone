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


if __name__ == "__main__":
    test_text = (
        "i saw a hostile crowd at the station did you mean hostel or hostile i asked"
    )
    result = main(test_text)
    print(f"Result: {result}")
