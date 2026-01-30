from pathlib import Path

import getpass
import os
import subprocess
import typer
from pydantic import BaseModel
from pydantic_evals import Dataset
from rich.console import Console
from rich.table import Table
from dotenv import load_dotenv
load_dotenv()

app = typer.Typer(no_args_is_help=True, help="Run evaluations for AI agent katas")
console = Console()


def _ensure_api_keys(required_keys: tuple[str, ...]) -> None:
    missing = [key for key in required_keys if not os.getenv(key)]
    if not missing:
        return

    console.print("[yellow]Missing API keys detected.[/yellow]")
    for key in missing:
        value = typer.prompt(f"Enter {key}", hide_input=True)
        if not value:
            console.print(f"[red]Error: {key} is required to continue.[/red]")
            raise typer.Exit(1)
        os.environ[key] = value


def _read_env_lines(env_path: Path) -> list[str]:
    if not env_path.exists():
        return []
    return env_path.read_text().splitlines()


def _upsert_env_line(lines: list[str], key: str, value: str) -> tuple[list[str], bool]:
    updated = False
    found = False
    new_lines: list[str] = []
    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            new_lines.append(line)
            continue

        prefix = ""
        candidate = stripped
        if stripped.startswith("export "):
            prefix = "export "
            candidate = stripped[len(prefix) :]

        if candidate.startswith(f"{key}="):
            found = True
            existing_value = candidate.split("=", 1)[1]
            if existing_value != value:
                new_lines.append(f"{prefix}{key}={value}")
                updated = True
            else:
                new_lines.append(line)
            continue

        new_lines.append(line)

    if not found:
        new_lines.append(f"{key}={value}")
        updated = True

    return new_lines, updated


def _write_env_file(env_path: Path, lines: list[str]) -> None:
    content = "\n".join(lines).rstrip("\n") + "\n"
    env_path.write_text(content)


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


@app.command("start")
def onboard() -> None:
    """Interactive setup for API keys."""
    env_path = Path(".env")
    lines = _read_env_lines(env_path)
    updated = False

    required_keys = ("GEMINI_API_KEY", "ANTHROPIC_API_KEY")


    for key in required_keys:
        value = os.getenv(key)
        if not value:
            value = typer.prompt(f"Enter {key}", hide_input=True)
        if not value:
            console.print(f"[red]Error: {key} is required to continue.[/red]")
            raise typer.Exit(1)

        lines, did_update = _upsert_env_line(lines, key, value)
        updated = updated or did_update
        os.environ[key] = value

    

    if updated or not env_path.exists():
        _write_env_file(env_path, lines)
        console.print(f"[green]Saved API keys to {env_path}[/green]")
    else:
        console.print("[green]API keys already configured.[/green]")

    should_create_branch = typer.confirm("Create a git branch now?", default=True)
    if not should_create_branch:
        return

    default_branch = f"user/{getpass.getuser()}"
    branch_name = typer.prompt("Branch name", default=default_branch)
    if not branch_name:
        console.print("[red]Error: branch name is required.[/red]")
        raise typer.Exit(1)

    try:
        subprocess.run(
            ["git", "rev-parse", "--is-inside-work-tree"],
            check=True,
            capture_output=True,
            text=True,
        )
    except subprocess.CalledProcessError:
        console.print("[yellow]Not a git repository; skipping branch creation.[/yellow]")
        return

    try:
        current_branch = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()

        if current_branch == branch_name:
            console.print(f"[green]Already on branch {branch_name}.[/green]")
            return

        exists = subprocess.run(
            ["git", "show-ref", "--verify", "--quiet", f"refs/heads/{branch_name}"],
            capture_output=True,
            text=True,
        ).returncode == 0

        if exists:
            subprocess.run(["git", "checkout", branch_name], check=True)
            console.print(f"[green]Switched to branch {branch_name}.[/green]")
        else:
            subprocess.run(["git", "checkout", "-b", branch_name], check=True)
            console.print(f"[green]Created and switched to {branch_name}.[/green]")
    except subprocess.CalledProcessError as exc:
        console.print(f"[red]Git error while creating branch: {exc}[/red]")


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


@app.command()
def assess(
    project_path: Path | None = typer.Argument(
        None, help="Path to the project directory to assess"
    ),
    output: Path | None = typer.Option(
        None,
        "--output",
        "-o",
        help="Output HTML file path (JSON will use same name with .json extension)",
    ),
    output_dir: Path = typer.Option(
        "assessment_reports",
        "--output-dir",
        help="Base directory for assessment reports (default: assessment_reports)",
    ),
):
    """Assess agent, MCP, RAG, or capstone projects and generate HTML/JSON reports."""
    _ensure_api_keys(("GEMINI_API_KEY",))
    from src.assessor.main import assess as assessor_assess

    resolved_output_dir = output_dir
    kind_normalized: str | None = None
    if project_path is not None:
        kind_candidates = {
            "mcp_katas": "mcp",
            "katas": "agent",
            "rag": "rag",
            "rag_katas": "rag",
            "capstone": "capstone",
        }
        kind_normalized = next(
            (kind_value for folder, kind_value in kind_candidates.items() if folder in project_path.parts),
            None,
        )

    if kind_normalized is not None and kind_normalized in {"agent", "mcp", "rag", "capstone"}:
        resolved_output_dir = output_dir / kind_normalized

    assessor_assess(
        project_path=project_path,
        output=output,
        output_dir=resolved_output_dir,
    )


if __name__ == "__main__":
    app()