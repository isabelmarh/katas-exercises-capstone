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
    agent_file: Path


def discover_katas(workspace_path: Path = Path("katas")) -> list[KataConfig]:
    if not workspace_path.exists():
        return []

    agent_files = [file for file in workspace_path.rglob("main.py") if file.exists()]
    return [
        KataConfig(
            name=agent_file.relative_to(workspace_path).parts[0],
            path=agent_file.parent,
            agent_file=agent_file,
        ) for agent_file in agent_files
    ]


def load_agent_function_from_file(agent_file: Path):
    import importlib.util
    import sys

    mod_name = f"{agent_file.stem}_{hash((agent_file, agent_file.stat().st_mtime_ns))}"
    spec = importlib.util.spec_from_file_location(mod_name, agent_file)
    if spec is None or spec.loader is None:
        raise ValueError(f"Could not load agent from {agent_file}")

    module = importlib.util.module_from_spec(spec)
    sys.modules[mod_name] = module
    spec.loader.exec_module(module)

    # Check for inline evaluations (dataset ending with _dataset)
    dataset_attrs = [attr for attr in dir(module) if attr.endswith("_dataset")]
    if dataset_attrs and hasattr(module, "main"):
        dataset = getattr(module, dataset_attrs[0])
        main_fn = module.main
        return (dataset, main_fn), True  # True indicates inline evals

    # Preferred: a PydanticAI Agent object named `agent`
    if hasattr(module, "agent"):
        agent = module.agent

        def agent_function(inputs: str) -> str:
            # sync all the way: avoids per-case event loop churn
            res = agent.run_sync(inputs)
            return res.output

        return agent_function, False

    # Fallback: a plain sync callable `main(inputs) -> str`
    if hasattr(module, "main"):
        main_fn = module.main
        if callable(main_fn):
            return main_fn, False

    raise ValueError(f"No agent, main function, or dataset found in {agent_file}")


@app.command()
def list_katas() -> None:
    katas = discover_katas()
    if not katas:
        console.print("[red]No katas found![/red]")
        return

    table = Table(title="Available Katas")
    table.add_column("Name", style="cyan")
    table.add_column("Path", style="magenta")
    table.add_column("Has Evals", style="green")

    for kata in katas:
        has_evals = "✓"  # if kata.evals_file.stat().st_size > 0 else "✗"
        table.add_row(kata.name, str(kata.path), has_evals)

    console.print(table)


@app.command()
def run(
    kata_name: str | None = typer.Argument(None, help="Name of the kata to run"),
) -> None:
    katas = discover_katas()
    if not katas:
        console.print("[red]No katas found![/red]")
        raise typer.Exit(1)

    if kata_name is None:
        console.print("[blue]Available katas:[/blue]")
        for i, kata in enumerate(katas, 1):
            has_evals = "✓"  # if kata.evals_file.stat().st_size > 0 else "✗"
            console.print(f"  {i}. {kata.name} {has_evals}")

        choice = typer.prompt("Select kata number")
        try:
            selected_index = int(choice) - 1
            kata = katas[selected_index]
        except (ValueError, IndexError):
            console.print("[red]Invalid selection![/red]")
            raise typer.Exit(1)
    else:
        kata = next((k for k in katas if k.name == kata_name), None)
        if not kata:
            console.print(f"[red]Kata '{kata_name}' not found![/red]")
            raise typer.Exit(1)

    console.print(f"[blue]Loading agent from {kata.agent_file}...[/blue]")
    agent_function_or_runner, has_inline_evals = load_agent_function_from_file(
        kata.agent_file
    )

    if has_inline_evals:
        console.print(f"[blue]Running inline evaluations for {kata.name}...[/blue]")
        dataset, main_fn = agent_function_or_runner
        report = dataset.evaluate_sync(main_fn)
        console.print("[green]Evaluation complete![/green]")
        report.print(include_input=True, include_output=True, include_expected_output=True)
        return

    if kata.evals_file.stat().st_size == 0:
        console.print(f"[red]Evals file for '{kata.name}' is empty![/red]")
        raise typer.Exit(1)

    console.print(f"[blue]Loading evals for {kata.name}...[/blue]")
    dataset = Dataset.from_file(kata.evals_file)

    console.print(f"[blue]Running {len(dataset.cases)} evaluations...[/blue]")

    def run_agent(inputs: str) -> str:
        # Synchronous path only; agent_function already uses run_sync when needed
        return agent_function_or_runner(inputs)

    report = dataset.evaluate_sync(run_agent)

    console.print("[green]Evaluation complete![/green]")
    report.print(include_input=True, include_output=True, include_expected_output=True)


if __name__ == "__main__":
    app()
