from __future__ import annotations

from typing import Any

from pydantic_evals import Case, Dataset
from pydantic_evals.evaluators import LLMJudge


def main(workflow_yaml: str) -> str:
    """
    GitHub Actions Job Namer Agent

    Rename GitHub Actions job IDs to match a standard taxonomy based on what
    each job actually does. Update any `needs:` references to use the new names.
    Do not change anything else (steps, triggers, permissions, etc.).

    Standard job names:
    - unit-test: fast, isolated tests (pytest, jest, vitest, go test, etc.)
    - integration-test: tests touching databases, APIs, or external services
    - smoke-test: quick sanity checks run after deployment
    - build: compiles code or produces a deployable artifact
    - lint: linters, formatters, or static analysis
    - deploy: deploys to an environment
    - publish: publishes a package to a registry
    - security-scan: security or vulnerability scanning

    If a job's purpose is unclear, keep the original name.

    Args:
        workflow_yaml: Raw GitHub Actions workflow YAML string

    Returns:
        Workflow YAML with job IDs renamed to the standard taxonomy
    """
    raise NotImplementedError("GitHub Actions job namer not implemented")


github_actions_dataset = Dataset[str, str, Any](
    cases=[
        Case(
            name="build-job-runs-tests",
            inputs="""\
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
""",
            expected_output="""\
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
""",
            evaluators=(
                LLMJudge(
                    rubric=(
                        "The 'build' job runs pytest so it must be renamed to 'unit-test'. "
                        "Nothing else should change."
                    ),
                ),
            ),
        ),
        Case(
            name="ci-job-runs-linter",
            inputs="""\
name: Lint
on:
  pull_request:
jobs:
  ci:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: npm run eslint
""",
            expected_output="""\
name: Lint
on:
  pull_request:
jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: npm run eslint
""",
            evaluators=(
                LLMJudge(
                    rubric=(
                        "The 'ci' job runs eslint so it must be renamed to 'lint'. "
                        "Nothing else should change."
                    ),
                ),
            ),
        ),
        Case(
            name="test-job-runs-playwright",
            inputs="""\
name: E2E
on:
  push:
    branches: [main]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: npx playwright test
""",
            expected_output="""\
name: E2E
on:
  push:
    branches: [main]
jobs:
  integration-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: npx playwright test
""",
            evaluators=(
                LLMJudge(
                    rubric=(
                        "The 'test' job runs Playwright (an end-to-end browser testing tool) "
                        "so it must be renamed to 'integration-test'. Nothing else should change."
                    ),
                ),
            ),
        ),
        Case(
            name="already-correctly-named",
            inputs="""\
name: Tests
on:
  push:
    branches: [main]
jobs:
  unit-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: pytest
""",
            expected_output="""\
name: Tests
on:
  push:
    branches: [main]
jobs:
  unit-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: pytest
""",
            evaluators=(
                LLMJudge(
                    rubric=(
                        "The job is already named 'unit-test' which is correct. "
                        "The output must be identical to the input."
                    ),
                ),
            ),
        ),
        Case(
            name="multiple-jobs-needs-updated",
            inputs="""\
name: Release
on:
  push:
    branches: [main]
jobs:
  compile:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: go build ./...
  check:
    runs-on: ubuntu-latest
    needs: compile
    steps:
      - uses: actions/checkout@v4
      - run: go test ./...
  ship:
    runs-on: ubuntu-latest
    needs: check
    steps:
      - uses: actions/checkout@v4
      - run: docker push myimage:latest
""",
            expected_output="""\
name: Release
on:
  push:
    branches: [main]
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: go build ./...
  unit-test:
    runs-on: ubuntu-latest
    needs: build
    steps:
      - uses: actions/checkout@v4
      - run: go test ./...
  publish:
    runs-on: ubuntu-latest
    needs: unit-test
    steps:
      - uses: actions/checkout@v4
      - run: docker push myimage:latest
""",
            evaluators=(
                LLMJudge(
                    rubric=(
                        "'compile' runs 'go build' so it must become 'build'. "
                        "'check' runs 'go test' so it must become 'unit-test' and its needs must update to 'build'. "
                        "'ship' pushes a Docker image so it must become 'publish' and its needs must update to 'unit-test'. "
                        "Nothing else should change."
                    ),
                ),
            ),
        ),
    ],
    evaluators=[
        LLMJudge(
            rubric=(
                "Job IDs must be renamed to the standard taxonomy "
                "(unit-test, integration-test, smoke-test, build, lint, deploy, publish, security-scan) "
                "based on what each job actually does. "
                "All needs: references must be updated to match the new job IDs. "
                "Nothing else should change."
            ),
        ),
    ],
)


if __name__ == "__main__":
    report = github_actions_dataset.evaluate_sync(main)
    report.print(include_input=True, include_output=True, include_expected_output=True)
