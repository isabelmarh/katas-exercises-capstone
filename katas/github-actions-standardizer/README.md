# GitHub Actions Job Namer Kata

## Goal

Build an AI agent that renames GitHub Actions jobs to follow a standard taxonomy based on what they actually do.

## Challenge

Job names like `build`, `ci`, `test`, or `check` are vague. Your agent must inspect what each job does and rename it to the closest standard name from this taxonomy:

| Job ID | When to use |
|---|---|
| `unit-test` | Fast, isolated tests (pytest, jest, vitest, go test, etc.) |
| `integration-test` | Tests that touch databases, APIs, or external services |
| `smoke-test` | Quick sanity checks run after deployment |
| `build` | Compiles code or produces a deployable artifact |
| `lint` | Linters, formatters, or static analysis |
| `deploy` | Deploys to an environment |
| `publish` | Publishes a package to a registry |
| `security-scan` | Security or vulnerability scanning |

Rules:
- Rename job IDs (the key in the `jobs:` map) to the closest matching standard name
- Update all `needs:` references to use the new name
- If you cannot determine the job type, keep the original name
- Do not change anything else — steps, triggers, permissions, etc. are out of scope

## Example Input

```yaml
name: CI
on:
  push:
    branches: [main]
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: pytest
```

## Example Output

```yaml
name: CI
on:
  push:
    branches: [main]
jobs:
  unit-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: pytest
```

## Steps

1. Implement the agent in `main.py` following the function signature
2. Run the evaluation suite: `uv run python main.py`
