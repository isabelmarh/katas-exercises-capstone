from __future__ import annotations

import os
from typing import Any

import yaml
from pydantic import AnyUrl
from pydantic_ai import Agent
from pydantic_evals import Case, Dataset

from katas.text_checker.evaluators import CorrectAssessmentEval, AmountFactsEval, SourceCredabilityEvals
from katas.text_checker.models import Assessment, Claim

agent = Agent(model="google-gla:gemini-2.5-pro")


def main(blip_description: str) -> Assessment:
    # result = agent.run_sync(blip_description)
    #
    return Assessment(
        rating="Hold",
        claims=[
            Claim(
                claim="asd",
                rating="TRUE",
                explanation="asd",
                sources=[
                    AnyUrl(
                        "https://martinfowler.com/articles/richardsonMaturityModel.html"
                    )
                ],
            )
        ],
    )


def load_blips_from_yaml(yaml_path: str) -> Dataset[str, Assessment, Any]:
    with open(yaml_path, "r") as f:
        data = yaml.safe_load(f)

    cases: list[Case] = []
    for item in data.get("blips", [])[0:1]:
        cases.append(
            Case(
                name=item["name"],
                inputs=item["description"],
                expected_output=item["rating"],
                metadata={},
                evaluators=(CorrectAssessmentEval(expected_rating=item["rating"]),),
            )
        )

    return Dataset[str, Assessment, Any](
        cases=cases,
        evaluators=[AmountFactsEval(number_facts=3), SourceCredabilityEvals()],
    )


vol32_blips_dataset = load_blips_from_yaml(
    os.path.join(os.path.dirname(__file__), "vol32_blips.yaml")
)

if __name__ == "__main__":
    report = vol32_blips_dataset.evaluate_sync(main)
    report.print(include_reasons=True)
