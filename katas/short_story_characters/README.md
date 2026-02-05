# Short Story Characters

## Goal

The goal of this Kata is to build an AI agent that analyzes short stories and extracts structured character information from them. This kata focuses on two key aspects:

1. **Structured Output Generation**: Instead of receiving plain text responses, the agent should return well-defined, structured data (objects/classes) that can be directly processed by code. This demonstrates how to move beyond simple string parsing to leveraging LLMs for structured information extraction.

2. **Advanced Evaluation Techniques**: The evaluation approach goes beyond simple exact-match assertions. This kata explores more sophisticated evaluation methods that can assess the quality and correctness of structured outputs, handling cases where multiple valid answers may exist or where semantic similarity matters more than exact matching.

The broader goal is to demonstrate best practices for extracting and validating structured data from unstructured text using AI agents.

## The Kata

You are provided with classic short stories (e.g., "The Coming-Out of Maggie" by O. Henry and "Lamb to the Slaughter" by Roald Dahl) located in the `short_stories/` directory. Your task is to build an agent that reads these stories and extracts main characters along with their attributes (name, profession, description, etc.) as structured objects that can be programmatically processed.

The agent skeleton is already set up with:
- A basic `Character` model with minimal fields
- A simple agent configuration
- An evaluation framework with test cases for two short stories
- A custom `ContainsCharacter` evaluator that validates extracted characters

## Challenge

Breakdown of the main challenges:

1. **Character Extraction**: Identify and extract all main characters from a given short story, including their names, roles, and characteristics.
2. **Structured Data Modeling**: Enhance the data structures (Pydantic models) to represent character information comprehensively - including last names, professions, descriptions, and potentially relationships.
3. **Semantic Evaluation**: Implement evaluation strategies that can assess the correctness of extracted character information without requiring exact string matches, accounting for variations in naming, synonymous descriptions, and different but equally valid interpretations.

## TODOs

The following tasks need to be completed (see `main.py` for implementation details):

### 1. Enhance the Character Model (lines 19-24)
- Add more fields to the `Character` class: `last_name`, `profession`, `description`, etc.
- Consider adding validation rules to see how the agent reacts to them (e.g., profession should be from a predefined list, description should be at least 20 characters long)

### 2. Improve the Agent Instructions (lines 27-31)
- Refine the agent instructions to guide it in extracting comprehensive character information
- Consider adding examples or specific guidance on what constitutes a "main character"

### 3. Implement Semantic Evaluation (lines 62-67)
- Complete the `ContainsCharacter.evaluate()` method to check `last_name`, `profession`, and `description` fields
- Exact match might be too strict - consider using fuzzy matching or checking for key phrases in the description instead of exact matches
- Explore different matching strategies (e.g., semantic similarity, keyword matching, etc.)

## How to run it?

* `short-story-characters`: runs the evaluation (which executes the agent)
