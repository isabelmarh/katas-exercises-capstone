from pathlib import Path

import typer
from pydantic import BaseModel
from pydantic_evals import Dataset
from rich.console import Console
from rich.table import Table

app = typer.Typer(no_args_is_help=True, help="Run evaluations for AI agent katas")
console = Console()


class KataConfig(BaseModel):
    name: str
    path: Path
    evals_file: Path
    agent_file: Path


def discover_katas(workspace_path: Path = Path("katas")) -> list[KataConfig]:
    katas = []
    if not workspace_path.exists():
        return katas

    for kata_dir in workspace_path.iterdir():
        if not kata_dir.is_dir():
            continue

        evals_file = kata_dir / "evals.yaml"
        agent_file = kata_dir / "main.py"

        if evals_file.exists() and agent_file.exists():
            katas.append(
                KataConfig(
                    name=kata_dir.name,
                    path=kata_dir,
                    evals_file=evals_file,
                    agent_file=agent_file,
                )
            )

    return katas


def load_agent_function_from_file(agent_file: Path):
    import importlib.util
    import sys

    spec = importlib.util.spec_from_file_location("agent_module", agent_file)
    if spec is None or spec.loader is None:
        raise ValueError(f"Could not load agent from {agent_file}")

    module = importlib.util.module_from_spec(spec)
    sys.modules["agent_module"] = module
    spec.loader.exec_module(module)

    if hasattr(module, "agent"):
        # If it's a pydantic-ai Agent, we need to wrap it in a function
        agent = module.agent

        async def agent_function(inputs):
            result = await agent.run(inputs)
            return result.output

        return agent_function
    elif hasattr(module, "main"):
        return module.main
    else:
        raise ValueError(f"No agent or main function found in {agent_file}")


@app.command()
def list_katas() -> None:
    """List all available katas."""
    katas = discover_katas()

    if not katas:
        console.print("[red]No katas found![/red]")
        return

    table = Table(title="Available Katas")
    table.add_column("Name", style="cyan")
    table.add_column("Path", style="magenta")
    table.add_column("Has Evals", style="green")

    for kata in katas:
        has_evals = "✓" if kata.evals_file.stat().st_size > 0 else "✗"
        table.add_row(kata.name, str(kata.path), has_evals)

    console.print(table)


@app.command()
def run(
    kata_name: str | None = typer.Argument(None, help="Name of the kata to run"),
    output_file: Path | None = typer.Option(
        None, "--output", "-o", help="Save results to file"
    ),
) -> None:
    """Run evaluations for a specific kata."""
    katas = discover_katas()

    if not katas:
        console.print("[red]No katas found![/red]")
        raise typer.Exit(1)

    if kata_name is None:
        # Show selection interface
        console.print("[blue]Available katas:[/blue]")
        for i, kata in enumerate(katas, 1):
            has_evals = "✓" if kata.evals_file.stat().st_size > 0 else "✗"
            console.print(f"  {i}. {kata.name} {has_evals}")

        choice = typer.prompt("Select kata number")
        try:
            selected_index = int(choice) - 1
            if selected_index < 0 or selected_index >= len(katas):
                raise ValueError()
            kata = katas[selected_index]
        except (ValueError, IndexError):
            console.print("[red]Invalid selection![/red]")
            raise typer.Exit(1)
    else:
        kata = next((k for k in katas if k.name == kata_name), None)
        if not kata:
            console.print(f"[red]Kata '{kata_name}' not found![/red]")
            raise typer.Exit(1)

    if kata.evals_file.stat().st_size == 0:
        console.print(f"[red]Evals file for '{kata.name}' is empty![/red]")
        raise typer.Exit(1)

    console.print(f"[blue]Loading evals for {kata.name}...[/blue]")
    # Load dataset from file using pydantic-evals
    dataset = Dataset.from_file(kata.evals_file)

    console.print(f"[blue]Loading agent from {kata.agent_file}...[/blue]")
    agent_function = load_agent_function_from_file(kata.agent_file)

    console.print(f"[blue]Running {len(dataset.cases)} evaluations...[/blue]")
    report = dataset.evaluate_sync(agent_function)

    console.print("[green]Evaluation complete![/green]")
    # Print the report
    report.print(include_input=True, include_output=True)

    if output_file:
        # Save results to file (pydantic-evals doesn't have a save method on reports)
        console.print(
            f"[blue]Results printed above - manual save to {output_file} not implemented yet[/blue]"
        )


if __name__ == "__main__":
    app()
