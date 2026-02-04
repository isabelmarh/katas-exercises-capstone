from pathlib import Path
from datetime import datetime
import csv
import re

import getpass
import os
import subprocess
import typer
import questionary
import json
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
        entries = [{"branch": branch, "label": ""} for branch in _parse_branches_text(raw)]

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
        ref = remote_ref if _git_ref_exists(repo_path, f"refs/remotes/{remote_ref}") else branch

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
            result = assessment_agent.run_sync(CAPSTONE_ASSESS_PROMPT, deps=capstone_path)
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

    save_summary = questionary.confirm("Save summary table to a text file?", default=True).ask()
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