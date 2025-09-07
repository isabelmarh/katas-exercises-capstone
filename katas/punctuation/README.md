# Punctuation and Capitalization Kata

## Goal

The goal of this kata is to build an AI agent that adds proper punctuation and capitalization to text while preserving all original words exactly as they appear.

## Challenge

Your agent must:
- Add punctuation marks: comma (,), period (.), and question mark (?)
- Apply correct capitalization for sentences, acronyms, and proper nouns
- Preserve every word, spelling, and word order from the original text
- Only make punctuation and capitalization changes - no other modifications allowed

## Steps

1. Check out the `evals.yaml` file to understand the test cases
2. Implement the agent in `main.py` following the function signature
3. Test your implementation against the evaluation criteria
4. Ensure your agent handles edge cases and validates its own output

## Constraints

- **Critical**: Do not modify, add, or remove any words
- Only insert `,`, `.`, `?` and apply capitalization
- Preserve original spelling even if incorrect
- Maintain exact word order

Start coding in `main.py` and test as you go!
