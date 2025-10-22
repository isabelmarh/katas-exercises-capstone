from __future__ import annotations

import os
from typing import Any

from katas.text_checker.agent import agent
from katas.text_checker.evaluations import load_evaluation


def main(blip_description: str) -> dict[str, Any]:
    result = agent.run_sync(blip_description)

    return result.output.model_dump()


if __name__ == "__main__":
    vol32_blips_dataset = load_evaluation(
        os.path.join(os.path.dirname(__file__), "vol32_blips.yaml")
    )

    report = vol32_blips_dataset.evaluate_sync(main)
    report.print(include_reasons=True)
