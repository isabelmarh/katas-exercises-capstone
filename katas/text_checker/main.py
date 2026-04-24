import os
import sys
from pathlib import Path

# Ensure this directory is importable
sys.path.insert(0, str(Path(__file__).parent))

from evaluations import main as eval_main, run_agent, load_evaluation
from agent import agent

vol32_blips_dataset = load_evaluation(
    os.path.join(os.path.dirname(__file__), "vol32_blips.yaml")
)


def run_evals():
    report = vol32_blips_dataset.evaluate_sync(run_agent)
    report.print(include_reasons=True)


if __name__ == "__main__":
    eval_main()
