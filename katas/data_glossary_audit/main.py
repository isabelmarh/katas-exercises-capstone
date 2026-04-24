from __future__ import annotations
from typing import Any
from pydantic_evals import Case, Dataset
from pydantic_evals.evaluators import EqualsExpected
from pydantic_ai import Agent

agent = Agent(
    model="anthropic:claude-sonnet-4-5",
    instructions="""You are a Data Glossary Audit Agent that evaluates data glossary definitions against strict quality criteria.

CRITICAL: Your response must be EXACTLY one word: "pass" or "fail". No explanations, no other text.

A definition PASSES only if it meets ALL of these criteria:
1. Singular form - uses singular nouns, not plural forms
2. Positive definition - states what it IS, not what it is NOT
3. Descriptive phrase or sentence - more than just a single word or bare term (must have at least a phrase with context)
4. Common abbreviations only - uses widely recognized abbreviations like "API", "HTTP", "HTTP/2", "TCP/IP", "USA", "CEO". Exclude obscure or specialized jargon acronyms. Technical definitions that properly use common abbreviations can pass this criterion.
5. No embedded definitions - doesn't parenthetically or explicitly define other concepts within the same definition
6. States essential meaning - captures the core concept or purpose (for technical terms, describing key technical attributes counts)
7. Precise and unambiguous - clear and specific language, not vague or unclear
8. Concise - appropriately brief without being excessively long or verbose
9. Able to stand alone - doesn't reference "above", "below", "as mentioned", or require external context
10. No procedural information - doesn't describe steps or creation processes; technical descriptions of what something IS or uses are acceptable
11. No circular reasoning - doesn't define something in terms of itself
12. Consistent terminology - uses standard terms consistently
13. Appropriate definition type - describes the concept itself, not example values or amounts

A definition FAILS if it violates ANY of the 13 criteria above.

Remember: Output must be exactly one word - either "pass" or "fail". Nothing else.
"""
)


def main(inputs: str) -> str:
    """
    Evaluate a data glossary definition against quality criteria.

    This function analyzes the provided definition to ensure it meets all
    quality standards for data glossary entries and returns a pass/fail result.

    Args:
        inputs: The definition text to evaluate

    Returns:
        "pass" if the definition meets all quality standards, "fail" otherwise
    """
    result = agent.run_sync(inputs)
    return result.output.strip()


# Evaluation dataset
data_glossary_audit_dataset = Dataset[str, str, Any](
    cases=[
        Case(
            name="singular_form",
            inputs="Customer data records information",
            expected_output="fail",
            metadata={
                "description": "Should be stated in singular form",
                "criterion": "singular",
            },
            evaluators=(EqualsExpected(),),
        ),
        Case(
            name="positive_definition",
            inputs="A user account is not a guest session",
            expected_output="fail",
            metadata={
                "description": "Should state what concept is, not what it is not",
                "criterion": "positive_definition",
            },
            evaluators=(EqualsExpected(),),
        ),
        Case(
            name="descriptive_phrase",
            inputs="Revenue",
            expected_output="fail",
            metadata={
                "description": "Should be descriptive phrase or sentence",
                "criterion": "descriptive",
            },
            evaluators=(EqualsExpected(),),
        ),
        Case(
            name="common_abbreviations",
            inputs="An API that uses HTTP/2 protocol via TCP/IP",
            expected_output="pass",
            metadata={
                "description": "Should contain only commonly understood abbreviations",
                "criterion": "abbreviations",
            },
            evaluators=(EqualsExpected(),),
        ),
        Case(
            name="no_embedded_definitions",
            inputs="A customer record (which is a structured data entry containing personal information) that tracks purchases",
            expected_output="fail",
            metadata={
                "description": "Should not embed definitions of other concepts",
                "criterion": "no_embedded_definitions",
            },
            evaluators=(EqualsExpected(),),
        ),
        Case(
            name="essential_meaning",
            inputs="A user account is a digital identity used for authentication and authorization",
            expected_output="pass",
            metadata={
                "description": "Should state essential meaning of concept",
                "criterion": "essential_meaning",
            },
            evaluators=(EqualsExpected(),),
        ),
        Case(
            name="precise_unambiguous",
            inputs="A thing that holds stuff",
            expected_output="fail",
            metadata={
                "description": "Should be precise and unambiguous",
                "criterion": "precision",
            },
            evaluators=(EqualsExpected(),),
        ),
        Case(
            name="concise",
            inputs="A customer record is a comprehensive digital repository that extensively documents and maintains detailed information about individual customers including but not limited to their personal details, contact information, purchase history, preferences, and various other data points",
            expected_output="fail",
            metadata={"description": "Should be concise", "criterion": "conciseness"},
            evaluators=(EqualsExpected(),),
        ),
        Case(
            name="standalone",
            inputs="A payment method as described above",
            expected_output="fail",
            metadata={
                "description": "Should be able to stand alone",
                "criterion": "standalone",
            },
            evaluators=(EqualsExpected(),),
        ),
        Case(
            name="no_procedural_info",
            inputs="A user account created by filling out the registration form and clicking submit",
            expected_output="fail",
            metadata={
                "description": "Should not embed procedural information",
                "criterion": "no_procedural",
            },
            evaluators=(EqualsExpected(),),
        ),
        Case(
            name="no_circular_reasoning",
            inputs="A customer is someone who is a customer of our business",
            expected_output="fail",
            metadata={
                "description": "Should avoid circular reasoning",
                "criterion": "no_circular",
            },
            evaluators=(EqualsExpected(),),
        ),
        Case(
            name="appropriate_type",
            inputs="Revenue: $1,234,567",
            expected_output="fail",
            metadata={
                "description": "Should be appropriate definition type, not example value",
                "criterion": "appropriate_type",
            },
            evaluators=(EqualsExpected(),),
        ),
    ],
    evaluators=[],
)


if __name__ == "__main__":
    report = data_glossary_audit_dataset.evaluate_sync(main)
    report.print()
