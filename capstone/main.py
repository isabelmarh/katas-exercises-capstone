from pathlib import Path

from app import run_query


def main() -> None:
    print("Career Compass Second Brain")
    print(f"Project root: {Path(__file__).resolve().parent}")

    while True:
        user_input = input("\nAsk a career question (or 'exit'): ").strip()
        if user_input.lower() in {"exit", "quit"}:
            break
        if not user_input:
            continue

        response = run_query(user_input)
        print(f"\n{response}")


if __name__ == "__main__":
    main()
