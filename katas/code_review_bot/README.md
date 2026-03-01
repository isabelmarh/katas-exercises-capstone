# Code Review Bot Kata

This kata challenges you to build an AI agent that analyzes code diffs and provides constructive review feedback.

## Challenge

Implement the `main()` function in `main.py` to analyze code changes and identify:

- **Security vulnerabilities** (SQL injection, XSS, etc.)
- **Performance issues** (N+1 queries, inefficient algorithms)
- **Code quality** (naming, complexity, duplication)
- **Best practices** for the language/framework
- **Potential bugs** or edge cases
- **Error handling** and logging concerns

## Guidelines

- Be constructive and specific
- Suggest concrete improvements
- Explain the "why" behind suggestions
- Highlight both issues and good practices
- Consider maintainability and readability

## Running the Kata

```bash
python main.py
```

This will run the evaluation suite to test your implementation against various code review scenarios.

## Evaluation Criteria

Your agent will be evaluated on its ability to:
- Identify common security vulnerabilities
- Spot performance problems like N+1 queries
- Recognize code quality issues
- Provide actionable feedback
- Give positive reinforcement for good practices
