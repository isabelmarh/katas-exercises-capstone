from __future__ import annotations

import json
import sys
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.append(str(Path(__file__).resolve().parent.parent))
    from app import run_query, run_query_with_metadata
    from agents.baseline_agent import generate_baseline_response
else:
    from ..app import run_query, run_query_with_metadata
    from ..agents.baseline_agent import generate_baseline_response

from .datasets import career_dataset
from .evaluators import (
    ActionabilityEvaluator,
    GroundednessEvaluator,
    PersonalizationEvaluator,
    PiiLeakageEvaluator,
    RetrievalPresenceEvaluator,
)


EVALUATORS = (
    ActionabilityEvaluator(),
    GroundednessEvaluator(),
    PersonalizationEvaluator(),
    PiiLeakageEvaluator(),
    RetrievalPresenceEvaluator(),
)


def baseline_system(query: str) -> str:
    return generate_baseline_response(query)


def full_system(query: str) -> str:
    return run_query(query)


def report_to_dict(report) -> dict[str, object]:
    averages = report.averages()
    return {
        "name": report.name,
        "scores": averages.scores if averages else {},
        "failures": len(report.failures),
        "cases": [
            {
                "name": case.name,
                "scores": {name: result.value for name, result in case.scores.items()},
                "assertions": {
                    name: result.value for name, result in case.assertions.items()
                },
            }
            for case in report.cases
        ],
    }


def write_evaluation_artifacts(baseline_report, full_report) -> Path:
    """Persist reproducible evaluation results for the capstone report."""
    report_dir = Path(__file__).resolve().parent / "reports"
    report_dir.mkdir(parents=True, exist_ok=True)

    json_path = report_dir / "latest_results.json"
    md_path = report_dir / "latest_results.md"

    payload = {
        "baseline": report_to_dict(baseline_report),
        "full_system": report_to_dict(full_report),
    }
    json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    baseline_scores = payload["baseline"]["scores"]
    full_scores = payload["full_system"]["scores"]
    lines = [
        "# Career Compass Evaluation Results",
        "",
        "| Metric | Baseline | Full System |",
        "| --- | ---: | ---: |",
    ]
    for metric in sorted(set(baseline_scores) | set(full_scores)):
        baseline_value = float(baseline_scores.get(metric, 0.0))
        full_value = float(full_scores.get(metric, 0.0))
        lines.append(f"| {metric} | {baseline_value:.2f} | {full_value:.2f} |")
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return md_path


def print_summary(name: str, report) -> None:
    averages = report.averages()
    print(f"\n{name} averages")
    if averages:
        for metric, value in averages.scores.items():
            print(f"- {metric}: {value:.2f}")
    else:
        print("- No aggregate metrics were produced.")
    if report.failures:
        print(f"- failures: {len(report.failures)}")


def run() -> None:
    print("Career Compass Pydantic Evals")

    baseline_dataset = career_dataset.model_copy(update={"evaluators": list(EVALUATORS)})
    full_dataset = career_dataset.model_copy(update={"evaluators": list(EVALUATORS)})

    baseline_report = baseline_dataset.evaluate_sync(baseline_system)
    full_report = full_dataset.evaluate_sync(full_system)

    print_summary("Baseline", baseline_report)
    print_summary("Full system", full_report)
    artifact_path = write_evaluation_artifacts(baseline_report, full_report)
    print(f"\nSaved evaluation summary to {artifact_path}")


if __name__ == "__main__":
    run()
