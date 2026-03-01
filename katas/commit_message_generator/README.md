# Commit Message Generator Kata

This kata challenges you to build an AI agent that analyzes code diffs and generates clear, informative commit messages following the conventional commit format.

## Challenge

Implement the `main()` function in `main.py` to analyze code changes and generate commit messages in the format:

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

## Commit Types

- **feat**: A new feature
- **fix**: A bug fix  
- **docs**: Documentation only changes
- **style**: Changes that do not affect meaning (formatting, etc)
- **refactor**: Code change that neither fixes a bug nor adds a feature
- **perf**: Code change that improves performance
- **test**: Adding missing tests or correcting existing tests
- **build**: Changes to build system or external dependencies
- **ci**: Changes to CI configuration files and scripts
- **chore**: Other changes that don't modify src or test files

## Guidelines

- Use present tense ("add feature" not "added feature")
- Keep subject line under 50 characters
- Capitalize subject line
- Don't end subject line with period
- Use body to explain what and why, not how
- Include breaking change info in footer if applicable

## Running the Kata

```bash
python main.py
```

This will run the evaluation suite to test your implementation against various code change scenarios.

## Evaluation Criteria

Your agent will be evaluated on its ability to:
- Correctly identify the type of change (feat, fix, refactor, etc.)
- Generate appropriate scope when applicable
- Create clear, concise descriptions
- Follow conventional commit format
- Capture the essence of the code changes
