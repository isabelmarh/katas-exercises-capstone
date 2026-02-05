from pathlib import Path
from datetime import datetime
import csv
import re

import getpass
import subprocess
from typing import Callable
from attr import dataclass
from pydantic_ai import Agent
import typer
import questionary
import json
from pydantic import BaseModel
from pydantic_evals import Dataset
from rich.console import Console
from rich.table import Table
import uvicorn

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
        )
        for agent_file in agent_files
    ]


@dataclass
class KataFunction:
    """
    This class represents the loaded agent function and its associated dataset (if any) for a kata.
    agent - the Agent object if defined in the agent file (preferred)
    main - the main function if defined in the agent file (fallback)
    dataset - the Dataset object if inline evaluations are defined in the agent file (dataset variable ending with _dataset)
    run_evals - a callable that takes the agent function and runs the evaluations, either using the inline dataset or the evals file, and returns the report
    """

    agent: Agent | None = None
    main_fn: Callable[[str], str] | None = None
    dataset: Dataset | None = None
    run_evals: Callable[[], None] | None = None

    def execute_evals(self) -> None:
        if self.run_evals:
            console.print("[blue]Running evaluations...[/blue]")
            self.run_evals()
            return

        run_agent: Callable[[str], str] | None = None

        if self.main_fn is not None:
            run_agent = self.main_fn
        elif self.agent is not None:
            agent = self.agent
            run_agent = lambda s: agent.run_sync(s).output

        if run_agent is None:
            console.print(
                "[red]No agent function or dataset defined for this kata![/red]"
            )
            typer.Exit(1)
            return

        if self.dataset is None:
            console.print("[red]No dataset defined for this kata![/red]")
            typer.Exit(1)
            return

        console.print("[blue]Running evaluations...[/blue]")
        report = self.dataset.evaluate_sync(run_agent)
        console.print("[green]Evaluation complete![/green]")
        report.print(
            include_input=True, include_output=True, include_expected_output=True
        )


def load_agent_function_from_file(kata: KataConfig) -> KataFunction:
    import importlib.util
    import sys

    console.print(f"[blue]Loading agent from {kata.agent_file}...[/blue]")

    mod_name = f"{kata.agent_file.stem}_{hash((kata.agent_file, kata.agent_file.stat().st_mtime_ns))}"
    spec = importlib.util.spec_from_file_location(mod_name, kata.agent_file)
    if spec is None or spec.loader is None:
        raise ValueError(f"Could not load agent from {kata.agent_file}")

    module = importlib.util.module_from_spec(spec)
    sys.modules[mod_name] = module
    spec.loader.exec_module(module)

    kata_function = KataFunction()

    # Check for inline evaluations (dataset ending with _dataset)
    dataset_attrs = [attr for attr in dir(module) if attr.endswith("_dataset")]
    if dataset_attrs:
        dataset = getattr(module, dataset_attrs[0])
        kata_function.dataset = dataset

    # Preferred: a PydanticAI Agent object named `agent`
    if hasattr(module, "agent"):
        kata_function.agent = module.agent

    # Fallback: a plain sync callable `main(inputs) -> str`
    if hasattr(module, "main"):
        if callable(module.main):
            kata_function.main_fn = module.main  # pyright: ignore[reportAttributeAccessIssue]

    # Fallback: a plain sync callable `main(inputs) -> str`
    if hasattr(module, "run_evals"):
        if callable(module.run_evals):
            kata_function.run_evals = module.run_evals  # pyright: ignore[reportAttributeAccessIssue]

    if not (kata_function.agent or kata_function.main_fn):
        raise ValueError("No agent, main function")

    return kata_function


@app.command(name="list")
@app.command(name="list-katas")
def list_katas() -> None:
    """List all available katas in the workspace."""
    katas = discover_katas()
    if not katas:
        console.print("[red]No katas found![/red]")
        return

    table = Table(title="Available Katas")
    table.add_column("Name", style="cyan")
    table.add_column("Path", style="magenta")
    table.add_column("Has Evals", style="green")

    for kata in katas:
        has_evals = "✓"  # if kata.katas.stat().st_size > 0 else "✗"
        table.add_row(kata.name, str(kata.path), has_evals)

    console.print(table)


@app.command("start")
def onboard() -> None:
    """Create a git branch to get started with the katas."""
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
        console.print(
            "[yellow]Not a git repository; skipping branch creation.[/yellow]"
        )
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

        exists = (
            subprocess.run(
                ["git", "show-ref", "--verify", "--quiet", f"refs/heads/{branch_name}"],
                capture_output=True,
                text=True,
            ).returncode
            == 0
        )

        if exists:
            subprocess.run(["git", "checkout", branch_name], check=True)
            console.print(f"[green]Switched to branch {branch_name}.[/green]")
        else:
            subprocess.run(["git", "checkout", "-b", branch_name], check=True)
            console.print(f"[green]Created and switched to {branch_name}.[/green]")
    except subprocess.CalledProcessError as exc:
        console.print(f"[red]Git error while creating branch: {exc}[/red]")


def _select_kata(kata_name: str | None) -> KataConfig:
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
    return kata


@app.command()
def run(
    kata_name: str | None = typer.Argument(None, help="Name of the kata to run"),
) -> None:
    """Run evaluations for a kata."""
    kata = _select_kata(kata_name)
    kata_function = load_agent_function_from_file(kata)
    kata_function.execute_evals()


@app.command()
def chat(
    kata_name: str | None = typer.Argument(None, help="Name of the kata to run"),
) -> None:
    """Open an interactive chat interface with the kata's agent."""
    kata = _select_kata(kata_name)
    kata_function = load_agent_function_from_file(kata)
    if kata_function.agent is None:
        console.print("[red]No agent defined for this kata![/red]")
        raise typer.Exit(1)
    kata_function.agent.to_cli_sync()


@app.command()
def web(
    kata_name: str | None = typer.Argument(None, help="Name of the kata to run"),
    port: int = typer.Option(8765, "--port", "-p", help="Port to run the web interface on"),
) -> None:
    """Start a web interface for the kata's agent."""
    kata = _select_kata(kata_name)
    kata_function = load_agent_function_from_file(kata)
    if kata_function.agent is None:
        console.print("[red]No agent defined for this kata![/red]")
        raise typer.Exit(1)
    app = kata_function.agent.to_web()

    console.print(f"[green]Starting web interface on http://0.0.0.0:{port}[/green]")
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="debug",
    )


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
            (
                kind_value
                for folder, kind_value in kind_candidates.items()
                if folder in project_path.parts
            ),
            None,
        )

    if kind_normalized is not None and kind_normalized in {
        "agent",
        "mcp",
        "rag",
        "capstone",
    }:
        resolved_output_dir = output_dir / kind_normalized

    assessor_assess(
        project_path=project_path,
        output=output,
        output_dir=resolved_output_dir,
    )


def _safe_dir_name(value: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9._-]+", "_", value.strip())
    return cleaned or "branch"


def _parse_branches_text(raw: str) -> list[str]:
    tokens: list[str] = []
    for line in raw.splitlines():
        tokens.extend(line.split(","))
    return [token.strip() for token in tokens if token.strip()]


def _read_branch_entries_from_file(file_path: Path) -> list[dict[str, str]]:
    if not file_path.exists():
        console.print(f"[red]Branch file not found: {file_path}[/red]")
        raise typer.Exit(1)

    content = file_path.read_text().splitlines()
    if not content:
        console.print(f"[red]Branch file is empty: {file_path}[/red]")
        raise typer.Exit(1)

    if file_path.suffix.lower() == ".csv" or any("," in line for line in content[:3]):
        entries: list[dict[str, str]] = []
        reader = csv.reader(content)
        for row in reader:
            if not row:
                continue
            cleaned = [cell.strip() for cell in row if cell.strip()]
            if not cleaned:
                continue
            header = ",".join(cleaned).lower()
            if "branch" in header and ("github" in header or "id" in header):
                continue
            if len(cleaned) == 1:
                entries.append({"branch": cleaned[0], "label": ""})
            else:
                entries.append({"label": cleaned[0], "branch": cleaned[1]})
        return entries

    branches = [line.strip() for line in content if line.strip()]
    return [{"branch": branch, "label": ""} for branch in branches]


def _git_ref_exists(repo_path: Path, ref: str) -> bool:
    return (
        subprocess.run(
            ["git", "show-ref", "--verify", "--quiet", ref],
            cwd=repo_path,
            capture_output=True,
        ).returncode
        == 0
    )


def _write_plain_summary(rows: list[dict[str, str]]) -> str:
    lines: list[str] = []
    for row in rows:
        parts = [
            f"Branch: {row.get('branch', 'N/A')}",
            f"Completed: {row.get('completed', 'No')}",
            f"Rating: {row.get('rating', 'N/A')}",
            f"Report: {row.get('report', 'N/A')}",
        ]
        lines.append(" | ".join(parts))
    return "\n".join(lines) + "\n"


@app.command("bulk-assess")
def bulk_assess() -> None:
    """Interactive admin actions for cohort assessments."""
    action = questionary.select(
        "Admin action",
        choices=[
            "Bulk assess branches (capstone only)",
            "Exit",
        ],
    ).ask()
    if action is None or action == "Exit":
        return

    repo_path_input = questionary.path(
        "Git repo path",
        default=str(Path.cwd()),
    ).ask()
    if not repo_path_input:
        return
    repo_path = Path(repo_path_input)

    try:
        subprocess.run(
            ["git", "rev-parse", "--is-inside-work-tree"],
            check=True,
            capture_output=True,
            cwd=repo_path,
            text=True,
        )
    except subprocess.CalledProcessError:
        console.print("[red]Not a git repository.[/red]")
        raise typer.Exit(1)

    branch_source = questionary.select(
        "How will you provide branches?",
        choices=["branches (comma-separated)", "Read from file"],
    ).ask()
    if branch_source is None:
        return

    entries: list[dict[str, str]]
    if branch_source == "Read from file":
        file_input = questionary.path(
            "Path to branches file (txt or csv)",
            default=str(repo_path / "branches.txt"),
        ).ask()
        if not file_input:
            return
        entries = _read_branch_entries_from_file(Path(file_input))
    else:
        raw = questionary.text(
            "Enter branches (comma separated)",
        ).ask()
        if not raw:
            return
        entries = [
            {"branch": branch, "label": ""} for branch in _parse_branches_text(raw)
        ]

    if not entries:
        console.print("[red]No branches provided.[/red]")
        raise typer.Exit(1)

    for entry in entries:
        if entry.get("label"):
            continue
        branch = entry["branch"]
        entry["label"] = branch

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    worktrees_base_input = questionary.path(
        "Worktrees base directory",
        default=str(repo_path / ".katas" / "admin-worktrees" / timestamp),
    ).ask()
    if not worktrees_base_input:
        return
    worktrees_base = Path(worktrees_base_input)
    worktrees_base.mkdir(parents=True, exist_ok=True)

    output_dir_input = questionary.path(
        "Report output directory",
        default=str(repo_path / "exports" / f"cohort_{timestamp}"),
    ).ask()
    if not output_dir_input:
        return
    output_dir = Path(output_dir_input)
    output_dir.mkdir(parents=True, exist_ok=True)

    proceed = questionary.confirm(
        f"Assess {len(entries)} branches and save reports to {output_dir}?",
        default=True,
    ).ask()
    if not proceed:
        return

    subprocess.run(["git", "fetch", "--all", "--prune"], cwd=repo_path, check=True)

    from src.assessor.main import CAPSTONE_ASSESS_PROMPT
    from src.assessor.agent import assessment_agent
    from src.assessor.html_generator import generate_html_report

    summary_rows: list[dict[str, str]] = []
    worktree_paths: list[Path] = []
    used_names: set[str] = set()

    for entry in entries:
        branch = entry["branch"]
        label = entry["label"]
        safe_label = _safe_dir_name(label)
        if safe_label in used_names:
            safe_label = f"{safe_label}_{len(used_names) + 1}"
        used_names.add(safe_label)

        worktree_path = worktrees_base / safe_label
        worktree_paths.append(worktree_path)

        remote_ref = branch if branch.startswith("origin/") else f"origin/{branch}"
        ref = (
            remote_ref
            if _git_ref_exists(repo_path, f"refs/remotes/{remote_ref}")
            else branch
        )

        try:
            subprocess.run(
                ["git", "worktree", "add", str(worktree_path), ref],
                cwd=repo_path,
                check=True,
                capture_output=True,
                text=True,
            )
        except subprocess.CalledProcessError as exc:
            console.print(f"[red]Failed to add worktree for {branch}: {exc}[/red]")
            summary_rows.append(
                {
                    "label": label,
                    "branch": branch,
                    "completed": "No",
                    "rating": "ERROR",
                    "report": "N/A",
                }
            )
            continue

        capstone_path = worktree_path / "capstone"
        if not capstone_path.exists():
            summary_rows.append(
                {
                    "label": label,
                    "branch": branch,
                    "completed": "No",
                    "rating": "N/A",
                    "report": "N/A",
                }
            )
            continue

        console.print(f"[cyan]Assessing {label} ({branch})...[/cyan]")
        try:
            result = assessment_agent.run_sync(
                CAPSTONE_ASSESS_PROMPT, deps=capstone_path
            )
            assessment = result.output
            student_dir = output_dir / safe_label
            student_dir.mkdir(parents=True, exist_ok=True)
            html_path = student_dir / "capstone_assessment.html"
            html_path.write_text(generate_html_report(assessment, label))

            json_path = student_dir / "capstone_assessment.json"
            json_data = assessment.model_dump(mode="json")
            json_data.pop("overall_score", None)
            json_path.write_text(json.dumps(json_data, indent=2))

            summary_rows.append(
                {
                    "label": label,
                    "branch": branch,
                    "completed": "Yes",
                    "rating": assessment.overall_rating.value,
                    "report": str(html_path.absolute()),
                }
            )
        except Exception as exc:
            console.print(f"[red]Assessment failed for {label}: {exc}[/red]")
            summary_rows.append(
                {
                    "label": label,
                    "branch": branch,
                    "completed": "No",
                    "rating": "ERROR",
                    "report": "N/A",
                }
            )

    table = Table(show_header=True, header_style="bold cyan")
    table.add_column("Branch")
    table.add_column("Completed")
    table.add_column("Rating")
    table.add_column("Report")
    for row in summary_rows:
        table.add_row(
            row.get("label", "N/A"),
            row.get("branch", "N/A"),
            row.get("completed", "No"),
            row.get("rating", "N/A"),
            row.get("report", "N/A"),
        )
    console.print(table)

    save_summary = questionary.confirm(
        "Save summary table to a text file?", default=True
    ).ask()
    if save_summary:
        default_path = output_dir / "cohort_summary.txt"
        summary_path = questionary.text(
            "Summary file path",
            default=str(default_path),
        ).ask()
        if summary_path:
            Path(summary_path).write_text(_write_plain_summary(summary_rows))
            console.print(f"[green]Saved summary to {summary_path}[/green]")

    cleanup = questionary.confirm("Remove worktrees now?", default=True).ask()
    if cleanup:
        for path in worktree_paths:
            try:
                subprocess.run(
                    ["git", "worktree", "remove", str(path)],
                    cwd=repo_path,
                    check=True,
                    capture_output=True,
                    text=True,
                )
            except subprocess.CalledProcessError:
                console.print(f"[yellow]Could not remove worktree: {path}[/yellow]")
        subprocess.run(["git", "worktree", "prune"], cwd=repo_path, check=True)


if __name__ == "__main__":
    app()