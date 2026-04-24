from .datasets import EVAL_CASES
from .evaluators import score_actionability


def run() -> None:
    print("Career Compass eval scaffold")
    for case in EVAL_CASES:
        summary = score_actionability(case["query"])
        print(f"{case['query']}: {summary.score:.2f} ({summary.passed})")


if __name__ == "__main__":
    run()
