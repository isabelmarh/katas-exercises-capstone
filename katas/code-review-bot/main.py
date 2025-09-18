from __future__ import annotations
from typing import Any
from pydantic_evals import Case, Dataset
from pydantic_evals.evaluators import LLMJudge


def main(code_diff: str) -> str:
    """
    Code Review Bot Agent

    This function should analyze a code diff and provide constructive review feedback.
    Focus on identifying issues and providing actionable suggestions.

    Review criteria to check:
    - Security vulnerabilities (SQL injection, XSS, etc.)
    - Performance issues (N+1 queries, inefficient algorithms)
    - Code quality (naming, complexity, duplication)
    - Best practices for the language/framework
    - Potential bugs or edge cases
    - Error handling and logging
    - Testing considerations

    Guidelines:
    - Be constructive and specific
    - Suggest concrete improvements
    - Explain the "why" behind suggestions
    - Highlight both issues and good practices
    - Consider maintainability and readability

    Args:
        code_diff: Git diff or code snippet to review

    Returns:
        Review feedback with specific line comments and suggestions
    """
    # TODO: Implement code review bot agent
    raise NotImplementedError("Code Review Bot agent not implemented")


# Evaluation dataset
code_review_dataset = Dataset[str, str, Any](
    cases=[
        Case(
            name="sql_injection_vulnerability",
            inputs="""+ def get_user(user_id):
+     query = f"SELECT * FROM users WHERE id = {user_id}"
+     return db.execute(query).fetchone()""",
            expected_output=None,
            metadata={"focus": "security", "vulnerability": "sql_injection"},
            evaluators=(
                LLMJudge(
                    rubric="Review should identify SQL injection vulnerability and suggest parameterized queries",
                    include_input=True,
                ),
            ),
        ),
        Case(
            name="performance_n_plus_one",
            inputs="""+ def get_user_posts(user_ids):
+     posts = []
+     for user_id in user_ids:
+         user_posts = db.query("SELECT * FROM posts WHERE user_id = ?", user_id)
+         posts.extend(user_posts)
+     return posts""",
            expected_output=None,
            metadata={"focus": "performance", "issue": "n_plus_one"},
            evaluators=(
                LLMJudge(
                    rubric="Review should identify N+1 query problem and suggest batch loading or JOIN",
                    include_input=True,
                ),
            ),
        ),
        Case(
            name="missing_error_handling",
            inputs="""+ def process_payment(amount, card_token):
+     charge = stripe.Charge.create(
+         amount=amount,
+         currency='usd',
+         source=card_token
+     )
+     return charge.id""",
            expected_output=None,
            metadata={"focus": "error_handling", "issue": "missing_exception_handling"},
            evaluators=(
                LLMJudge(
                    rubric="Review should identify missing error handling for payment processing and suggest try/catch",
                    include_input=True,
                ),
            ),
        ),
        Case(
            name="code_duplication",
            inputs="""+ def calculate_tax_us(amount):
+     base_rate = 0.08
+     state_rate = 0.02
+     return amount * (base_rate + state_rate)
+ 
+ def calculate_tax_canada(amount):
+     base_rate = 0.05
+     state_rate = 0.03
+     return amount * (base_rate + state_rate)""",
            expected_output=None,
            metadata={"focus": "code_quality", "issue": "duplication"},
            evaluators=(
                LLMJudge(
                    rubric="Review should identify code duplication and suggest extracting common tax calculation logic",
                    include_input=True,
                ),
            ),
        ),
        Case(
            name="poor_variable_naming",
            inputs="""+ def process_data(d):
+     x = []
+     for i in d:
+         if i['t'] == 'active':
+             y = i['v'] * 1.2
+             x.append(y)
+     return x""",
            expected_output=None,
            metadata={"focus": "readability", "issue": "poor_naming"},
            evaluators=(
                LLMJudge(
                    rubric="Review should identify poor variable naming and suggest descriptive names",
                    include_input=True,
                ),
            ),
        ),
        Case(
            name="good_practices",
            inputs="""+ def create_user(email: str, name: str) -> User:
+     '''Create a new user with validation.'''
+     if not email or '@' not in email:
+         raise ValueError("Invalid email address")
+     
+     if User.objects.filter(email=email).exists():
+         raise ValueError("User already exists")
+     
+     user = User.objects.create(
+         email=email.lower().strip(),
+         name=name.strip()
+     )
+     logger.info(f"Created user {user.id} with email {email}")
+     return user""",
            expected_output=None,
            metadata={"focus": "positive_feedback", "good_practices": ["validation", "logging", "type_hints"]},
            evaluators=(
                LLMJudge(
                    rubric="Review should recognize good practices like input validation, logging, and type hints",
                    include_input=True,
                ),
            ),
        ),
    ],
    evaluators=[
        LLMJudge(
            rubric="Review should be constructive, specific, and provide actionable feedback",
            include_input=True,
        ),
    ],
)


if __name__ == "__main__":
    report = code_review_dataset.evaluate_sync(main)
    report.print()
