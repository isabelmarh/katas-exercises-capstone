from pathlib import Path
import argparse
import sys

if __package__ in {None, ""}:
    sys.path.append(str(Path(__file__).resolve().parent))
    from app import run_query
    from agents.model_factory import active_model_label
    from agents.memory_agent import get_memory_store
    from env import load_local_env
else:
    from .app import run_query
    from .agents.model_factory import active_model_label
    from .agents.memory_agent import get_memory_store
    from .env import load_local_env


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Career Compass Second Brain")
    parser.add_argument("--query", help="Run a single query and exit.")
    parser.add_argument(
        "--no-memory",
        action="store_true",
        help="Disable preference and conversation memory for this run.",
    )
    parser.add_argument(
        "--reset-memory",
        action="store_true",
        help="Clear saved conversation history and preferences before running.",
    )
    return parser


def main() -> None:
    load_local_env()

    parser = build_parser()
    args = parser.parse_args()

    print("Career Compass Second Brain")
    print(f"Project root: {Path(__file__).resolve().parent}")
    print(f"Model mode: {active_model_label()}")

    if args.reset_memory:
        get_memory_store().reset()
        print("Memory reset.")

    if args.query:
        print()
        print(run_query(args.query, use_memory=not args.no_memory))
        return

    while True:
        user_input = input("\nAsk a career question (or 'exit'): ").strip()
        if user_input.lower() in {"exit", "quit"}:
            break
        if not user_input:
            continue

        response = run_query(user_input, use_memory=not args.no_memory)
        print(f"\n{response}")


if __name__ == "__main__":
    main()
