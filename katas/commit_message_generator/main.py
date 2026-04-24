from __future__ import annotations
from typing import Any
from pydantic_evals import Case, Dataset
from pydantic_evals.evaluators import LLMJudge
from pydantic_ai import Agent
from pydantic_evals.evaluators import EqualsExpected

agent = Agent(
    model='anthropic:claude-sonnet-4-5',
    instructions="""You are an expert at anlyzing code diffs and generating clear, informative commit messages following conventional commit format.
    
    Conventional Commit Format:
    <type>[optional scope]: <description>    

    COMMIT TYPES (choose ONE):
    - feat: A new feature
    - fix: A bug fix
    - docs: Documentation only changes
    - style: Changes that do not affect meaning (white-space, formatting, etc)
    - refactor: A code change that neither fixes a bug nor adds a feature
    - perf: A code change that improves performance
    - test: Adding missing tests or correcting existing tests
    - build: Changes that affect the build system or external dependencies
    - ci: Changes to CI configuration files and scripts
    - chore: Other changes that don't modify src or test files

    Guidelines:
    - Use present tense ("add feature" not "added feature")
    - Keep subject line under 50 characters
    - Capitalize subject line
    - Don't end subject line with period
    - Start with a verb: Add, Fix, Improve, Replace, Simplify, Implement, Update
    - Check format - "type(scope): description"
    - Return ONLY the subject line. No body, no explanation, no extra text.
    - Only include scope if it adds useful context. Don't add scope if it's obvious or not relevant.


    EXAMPLES OF GOOD COMMITS:
    - "feat(auth): Add password reset functionality" (new feature with scope)
    - "fix: Correct discount calculation formula" (bug fix, no scope needed)
    - "refactor(models): Simplify user name handling with properties" (refactoring)
    - "docs: Add authentication usage examples to README" (documentation)
    - "perf(database): Replace N+1 queries with single JOIN query" (performance)


    Args:
        code_diff: Git diff showing the changes made

    Returns:
        Well-formatted conventional commit message"""
    )


def main(code_diff: str) -> str:
    """
    Commit Message Generator Agent

    This function should analyze a code diff and generate a clear, informative
    commit message following conventional commit format.

    Conventional Commit Format:
    <type>[optional scope]: <description>

    [optional body]

    [optional footer(s)]

    Types:
    - feat: A new feature
    - fix: A bug fix
    - docs: Documentation only changes
    - style: Changes that do not affect meaning (white-space, formatting, etc)
    - refactor: A code change that neither fixes a bug nor adds a feature
    - perf: A code change that improves performance
    - test: Adding missing tests or correcting existing tests
    - build: Changes that affect the build system or external dependencies
    - ci: Changes to CI configuration files and scripts
    - chore: Other changes that don't modify src or test files

    Guidelines:
    - Use present tense ("add feature" not "added feature")
    - Keep subject line under 50 characters
    - Capitalize subject line
    - Don't end subject line with period
    - Use body to explain what and why, not how
    - Separate subject from body with blank line
    - Include breaking change info in footer if applicable

    Args:
        code_diff: Git diff showing the changes made

    Returns:
        Well-formatted conventional commit message
    """
    # TODO: Implement commit message generator agent

    result = agent.run_sync(code_diff)
    return result.output.strip()


commit_message_dataset = Dataset[str, str, Any](
    cases=[
        Case(
            name="feature_addition",
            inputs="+ def reset_password(self, email: str, new_password: str) -> bool:\n+     user = self.db.get_user_by_email(email)\n+     if not user:\n+         return False\n+     user.password = hash_password(new_password)\n+     self.db.save(user)\n+     return True",
            expected_output="feat(auth): Add password reset functionality",
            metadata={"type": "feature", "scope": "auth"},
            evaluators=(
                LLMJudge(
                    rubric="Commit message should identify this as a feature addition with appropriate type and scope",
                    model='anthropic:claude-sonnet-4-5'
                ),
            ),
        ),
        Case(
            name="bug_fix",
            inputs="-    return price * (discount_percent / 100)\n+    return price * (1 - discount_percent / 100)",
            expected_output="fix: Correct discount calculation formula",
            metadata={"type": "bugfix", "issue": "calculation_error"},
            evaluators=(
                LLMJudge(
                    rubric="Commit message should identify this as a bug fix and briefly describe the fix",
                    model='anthropic:claude-sonnet-4-5'
                ),
            ),
        ),
        Case(
            name="refactoring",
            inputs='-    def get_full_name(self):\n-        return f"{self.first_name} {self.last_name}"\n+    @property\n+    def full_name(self) -> str:\n+        return f"{self.first_name} {self.last_name}"',
            expected_output="refactor(models): Simplify user name handling with properties",
            metadata={"type": "refactor", "scope": "models"},
            evaluators=(
                LLMJudge(
                    rubric="Commit message should identify this as refactoring and mention the simplification",
                    model='anthropic:claude-sonnet-4-5'
                ),
            ),
        ),
        Case(
            name="documentation",
            inputs="+ ### Authentication\n+ The API uses JWT tokens for authentication:\n+ ```python\n+ headers = {'Authorization': f'Bearer {token}'}\n+ ```",
            expected_output="docs: Add authentication usage examples to README",
            metadata={"type": "documentation"},
            evaluators=(
                LLMJudge(
                    rubric="Commit message should identify this as documentation and mention what was added",
                    model='anthropic:claude-sonnet-4-5'
                ),
            ),
        ),
        Case(
            name="performance_improvement",
            inputs='-        for user_id in user_ids:\n-            user = self.db.query("SELECT * FROM users WHERE id = ?", user_id)\n-            posts = self.db.query("SELECT * FROM posts WHERE user_id = ?", user_id)\n+        return self.db.query("SELECT u.*, p.* FROM users u LEFT JOIN posts p ON u.id = p.user_id WHERE u.id IN (?)", user_ids)',
            expected_output="perf(database): Replace N+1 queries with single JOIN query",
            metadata={"type": "performance", "improvement": "query_optimization"},
            evaluators=(
                LLMJudge(
                    rubric="Commit message should identify this as performance improvement and mention query optimization",
                    model='anthropic:claude-sonnet-4-5'
                ),
            ),
        ),
    ],
    evaluators=[
        LLMJudge(
            rubric="Commit message should follow conventional commit format with appropriate type and clear description",
            model='anthropic:claude-sonnet-4-5'
        ),
    ],
)


if __name__ == "__main__":
    report = commit_message_dataset.evaluate_sync(main)
    report.print()
