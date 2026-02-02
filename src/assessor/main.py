import os
import typer
import questionary
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table
from dotenv import load_dotenv
from .agent import (
    assessment_agent,
    agent_kata_assessment_agent,
    rag_assessment_agent,
    mcp_assessment_agent,
)
from .models import AgentKataAssessment, MCPKataAssessment
from .html_generator import (
    generate_agent_kata_report,
    generate_html_report,
    generate_mcp_kata_report,
)
import json
import subprocess


app = typer.Typer(
    help="Capstone project assessment tool using Pydantic AI",
    no_args_is_help=True,
    add_completion=True,
)
console = Console()
load_dotenv()
CAPSTONE_ASSESS_PROMPT = (
    "Thoroughly assess this capstone project. Use your tools to explore the codebase "
    "systematically and gather evidence for each rubric category. Be thorough in checking "
    "for all required components."
)

RAG_ASSESS_PROMPT = (
    "Thoroughly assess this RAG project. Use your tools to explore the codebase "
    "systematically and gather evidence for each rubric category. Focus on the RAG "
    "pipeline, evaluation, and engineering quality."
)


def ensure_api_keys(
    required_keys: tuple[str, ...] = ("GEMINI_API_KEY", "ANTHROPIC_API_KEY"),
) -> None:
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


def _agent_file_prompt(relative_file: str) -> str:
    return (
        "Assess the Pydantic AI agent kata in the target file. "
        f"Target file: {relative_file}. Read this file first, then check any "
        "supporting code it imports."
    )


def _mcp_file_prompt(relative_file: str) -> str:
    return (
        "Assess the MCP server implementation in the target file. "
        f"Target file: {relative_file}. Read this file first, then check any "
        "supporting code it imports."
    )


@dataclass(frozen=True)
class AssessmentTarget:
    kind: str
    target_path: Path
    base_path: Path
    display_name: str
    relative_file: str | None = None


def _find_first_file(base_path: Path, filenames: list[str]) -> Path | None:
    for name in filenames:
        for candidate in base_path.rglob(name):
            if any(part.startswith(".") for part in candidate.parts):
                continue
            if "__pycache__" in str(candidate):
                continue
            return candidate
    return None


def _derive_display_name(file_path: Path) -> str:
    parent_name = file_path.parent.name
    if parent_name in {"katas", "mcp_katas"} and file_path.parent.parent != file_path.parent:
        return file_path.parent.parent.name
    return parent_name


def _resolve_assessment_targets(target_path: Path) -> list[AssessmentTarget]:
    targets: list[AssessmentTarget] = []

    if target_path.is_file():
        kind = "mcp" if "mcp_katas" in target_path.parts else "agent"
        display_name = _derive_display_name(target_path)
        relative_file = target_path.name
        base_path = target_path.parent

        # Preserve "single-file" behavior, but if the file lives under a kata folder like:
        #   .../katas/<kata_name>/py/main.py
        #   .../mcp_katas/<kata_name>/py/server.py
        # then scope deps + reporting to that specific <kata_name> folder.
        container_dir_name = "mcp_katas" if kind == "mcp" else "katas"
        container_dir: Path | None = None
        for parent in target_path.parents:
            if parent.name == container_dir_name:
                container_dir = parent
                break

        if container_dir is not None:
            try:
                rel_to_container = target_path.relative_to(container_dir)
            except ValueError:
                rel_to_container = None

            if rel_to_container is not None and len(rel_to_container.parts) >= 2:
                kata_name = rel_to_container.parts[0]
                kata_dir = container_dir / kata_name
                if kata_dir.is_dir():
                    base_path = kata_dir
                    display_name = kata_name
                    relative_file = str(target_path.relative_to(kata_dir))

        targets.append(
            AssessmentTarget(
                kind=kind,
                target_path=target_path,
                base_path=base_path,
                display_name=display_name,
                relative_file=relative_file,
            )
        )
        return targets

    if not target_path.is_dir():
        return targets

    root = target_path

    mcp_dir = root if root.name == "mcp_katas" else root / "mcp_katas"
    if not (mcp_dir.exists() and mcp_dir.is_dir()):
        for parent in root.parents:
            if parent.name == "mcp_katas":
                mcp_dir = parent
                break

    if mcp_dir.exists() and mcp_dir.is_dir():
        # Support multiple MCP katas under mcp_katas/<kata_name>/...
        subdirs: list[Path] = []
        if mcp_dir in root.parents and root != mcp_dir:
            try:
                rel_to_mcp = root.relative_to(mcp_dir)
            except ValueError:
                rel_to_mcp = None
            if rel_to_mcp is not None and rel_to_mcp.parts:
                kata_dir = mcp_dir / rel_to_mcp.parts[0]
                if kata_dir.is_dir():
                    subdirs = [kata_dir]

        if not subdirs:
            subdirs = [p for p in mcp_dir.iterdir() if p.is_dir() and not p.name.startswith(".")]
        if subdirs:
            for kata_dir in subdirs:
                mcp_file = _find_first_file(kata_dir, ["server.py", "main.py"])
                if not mcp_file:
                    continue
                targets.append(
                    AssessmentTarget(
                        kind="mcp",
                        target_path=mcp_file,
                        base_path=kata_dir,
                        display_name=kata_dir.name,
                        relative_file=str(mcp_file.relative_to(kata_dir)),
                    )
                )
        else:
            # Fallback to legacy layout with a single server.py/main.py directly under mcp_katas
            mcp_file = _find_first_file(mcp_dir, ["server.py", "main.py"])
            if mcp_file:
                targets.append(
                    AssessmentTarget(
                        kind="mcp",
                        target_path=mcp_file,
                        base_path=mcp_dir,
                        display_name=_derive_display_name(mcp_file),
                        relative_file=str(mcp_file.relative_to(mcp_dir)),
                    )
                )

    katas_dir = root if root.name == "katas" else root / "katas"
    if katas_dir.exists() and katas_dir.is_dir():
        # Support multiple agent katas under katas/<agent_name>/...
        subdirs = [p for p in katas_dir.iterdir() if p.is_dir() and not p.name.startswith(".")]
        if subdirs:
            for agent_dir in subdirs:
                agent_file = _find_first_file(agent_dir, ["main.py"])
                if not agent_file:
                    continue
                targets.append(
                    AssessmentTarget(
                        kind="agent",
                        target_path=agent_file,
                        base_path=agent_dir,
                        display_name=agent_dir.name,
                        relative_file=str(agent_file.relative_to(agent_dir)),
                    )
                )
        else:
            # Fallback to legacy layout with a single main.py directly under katas
            agent_file = _find_first_file(katas_dir, ["main.py"])
            if agent_file:
                targets.append(
                    AssessmentTarget(
                        kind="agent",
                        target_path=agent_file,
                        base_path=katas_dir,
                        display_name=_derive_display_name(agent_file),
                        relative_file=str(agent_file.relative_to(katas_dir)),
                    )
                )

    rag_dir = root if root.name == "rag" else root / "rag"
    if rag_dir.exists() and rag_dir.is_dir():
        targets.append(
            AssessmentTarget(
                kind="rag",
                target_path=rag_dir,
                base_path=rag_dir,
                display_name=rag_dir.name,
                relative_file=None,
            )
        )

    capstone_dir = root if root.name == "capstone" else root / "capstone"
    if capstone_dir.exists() and capstone_dir.is_dir():
        targets.append(
            AssessmentTarget(
                kind="capstone",
                target_path=capstone_dir,
                base_path=capstone_dir,
                display_name=capstone_dir.name,
                relative_file=None,
            )
        )

    if not targets:
        kind = "rag" if "rag" in root.name.lower() else "capstone"
        targets.append(
            AssessmentTarget(
                kind=kind,
                target_path=root,
                base_path=root,
                display_name=root.name,
                relative_file=None,
            )
        )

    return targets


def _select_assessment_target(targets: list[AssessmentTarget], kind: str) -> AssessmentTarget:
    if not targets:
        console.print("[red]Error: No assessable targets found.[/red]")
        raise typer.Exit(1)

    filtered = [t for t in targets if t.kind == kind]
    if not filtered:
        console.print(f"[red]No {kind} targets found.[/red]")
        raise typer.Exit(1)

    sorted_targets = sorted(filtered, key=lambda t: t.display_name)

    label_to_target: dict[str, AssessmentTarget] = {}
    for target in sorted_targets:
        label = f"[{target.kind}] {target.display_name}"
        label_to_target[label] = target

    selection = questionary.select(
        "Select target",
        choices=list(label_to_target.keys()),
    ).ask()
    if selection is None:
        raise typer.Exit(1)

    selected = label_to_target.get(selection)
    if selected is None:
        console.print("[red]Invalid selection![/red]")
        raise typer.Exit(1)
    return selected


def _select_project_folder(root: Path, kind: str) -> Path:
    if not root.exists():
        console.print(f"[red]Error: {root} does not exist[/red]")
        raise typer.Exit(1)

    if not root.is_dir():
        console.print(f"[red]Error: {root} must be a directory[/red]")
        raise typer.Exit(1)

    subdirs = [
        p
        for p in root.iterdir()
        if p.is_dir() and not p.name.startswith(".")
    ]
    if not subdirs:
        console.print(f"[yellow]No project folders found under {root}.[/yellow]")
        raise typer.Exit(1)

    sorted_subdirs = sorted(subdirs, key=lambda p: p.name.lower())
    selection = questionary.select(
        f"Select {kind} project",
        choices=[p.name for p in sorted_subdirs],
    ).ask()
    if selection is None:
        raise typer.Exit(1)

    for candidate in sorted_subdirs:
        if candidate.name == selection:
            return candidate

    console.print("[red]Invalid selection![/red]")
    raise typer.Exit(1)


def _write_agent_kata_reports(
    assessment: AgentKataAssessment,
    project_name: str,
    report_dir: Path,
) -> tuple[Path, Path]:
    """Write simplified reports for agent katas (no scores/ratings)."""
    report_dir.mkdir(parents=True, exist_ok=True)
    html_content = generate_agent_kata_report(assessment, project_name)
    html_path = report_dir / "assessment.html"
    html_path.write_text(html_content)

    json_path = report_dir / "assessment.json"
    json_data: dict[str, object] = assessment.model_dump(mode="json")
    json_path.write_text(json.dumps(json_data, indent=2))
    return html_path, json_path


def _write_mcp_kata_reports(
    assessment: MCPKataAssessment,
    project_name: str,
    report_dir: Path,
) -> tuple[Path, Path]:
    """Write simplified reports for MCP katas (no scores/ratings)."""
    report_dir.mkdir(parents=True, exist_ok=True)
    html_content = generate_mcp_kata_report(assessment, project_name)
    html_path = report_dir / "assessment.html"
    html_path.write_text(html_content)

    json_path = report_dir / "assessment.json"
    json_data: dict[str, object] = assessment.model_dump(mode="json")
    json_path.write_text(json.dumps(json_data, indent=2))
    return html_path, json_path


def _run_targets(
    targets: list[AssessmentTarget],
    output_dir: Path,
    output_override: Path | None = None,
) -> None:
    agent_map: dict[str, Any] = {
        "agent": agent_kata_assessment_agent,
        "mcp": mcp_assessment_agent,
        "rag": rag_assessment_agent,
        "capstone": assessment_agent,
    }

    for i, target in enumerate(targets, 1):
        console.print(
            f"\n[bold cyan][{i}/{len(targets)}] Assessing ({target.kind}):[/bold cyan] {target.display_name}"
        )
        console.print(f"[dim]Source: {target.target_path}[/dim]\n")

        if target.kind == "capstone":
            prompt = CAPSTONE_ASSESS_PROMPT
            deps = target.base_path
        elif target.kind == "rag":
            prompt = RAG_ASSESS_PROMPT
            deps = target.base_path
        elif target.kind == "agent":
            prompt = _agent_file_prompt(target.relative_file or target.target_path.name)
            deps = target.base_path
        elif target.kind == "mcp":
            prompt = _mcp_file_prompt(target.relative_file or target.target_path.name)
            deps = target.base_path
        else:
            console.print(f"[yellow]⊘ Unknown target type: {target.kind}[/yellow]\n")
            continue

        report_dir = target.base_path / "assessment_reports"
        if target.kind == "agent":
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
            ) as progress:
                task = progress.add_task(
                    "Agent exploring kata and generating feedback...", total=None
                )
                result = agent_kata_assessment_agent.run_sync(prompt, deps=deps)
                progress.update(task, completed=True)

            assessment = result.output
            html_path, json_path = _write_agent_kata_reports(
                assessment, target.display_name, report_dir
            )
            console.print("[bold green]✓[/bold green] Assessment complete!")
            console.print(f"[cyan]HTML report:[/cyan] {html_path.absolute()}")
            console.print(f"[cyan]JSON data:[/cyan] {json_path.absolute()}\n")
        elif target.kind == "mcp":
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
            ) as progress:
                task = progress.add_task(
                    "Agent exploring MCP server and generating feedback...", total=None
                )
                result = mcp_assessment_agent.run_sync(prompt, deps=deps)
                progress.update(task, completed=True)

            assessment = result.output
            html_path, json_path = _write_mcp_kata_reports(
                assessment, target.display_name, report_dir
            )
            console.print("[bold green]✓[/bold green] Assessment complete!")
            # console.print("[bold]Overall Rating:[/bold] N/A (feedback-only report)")
            console.print(f"[cyan]HTML report:[/cyan] {html_path.absolute()}")
            console.print(f"[cyan]JSON data:[/cyan] {json_path.absolute()}\n")
        else:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
            ) as progress:
                task = progress.add_task(
                    "Agent exploring codebase and running assessment...", total=None
                )
                agent = agent_map[target.kind]
                result = agent.run_sync(prompt, deps=deps)
                progress.update(task, completed=True)

            assessment = result.output
            if output_override is None:
                report_dir.mkdir(parents=True, exist_ok=True)
                html_path = report_dir / "assessment.html"
            else:
                html_path = output_override

            html_content = generate_html_report(assessment, target.display_name)
            html_path.write_text(html_content)

            json_path = html_path.with_suffix(".json")
            json_data = assessment.model_dump(mode="json")
            json_data.pop("overall_score", None)
            json_path.write_text(json.dumps(json_data, indent=2))

            console.print("[bold green]✓[/bold green] Assessment complete!")
            console.print(f"[bold]Overall Rating:[/bold] {assessment.overall_rating}")
            console.print(f"[cyan]HTML report:[/cyan] {html_path.absolute()}")
            console.print(f"[cyan]JSON data:[/cyan] {json_path.absolute()}\n")


@app.command()
def assess(
    project_path: Path | None = typer.Argument(
        None,
        help="Path to the project directory to assess",
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
    """
    Assess agent, MCP, RAG, or capstone projects and generate HTML/JSON reports.

    The agent will explore the codebase using tools to evaluate:
    - Multi-agent architecture with Pydantic AI
    - RAG implementation and vector storage
    - Memory systems and guardrails
    - OTEL observability
    - Evaluation framework with Pydantic Evals
    - Code quality and documentation
    """
    targets: list[AssessmentTarget] | None = None
    if project_path is None:
        all_targets = _resolve_assessment_targets(Path.cwd())
        if not all_targets:
            console.print("[red]Error: No assessable targets found.[/red]")
            raise typer.Exit(1)

        if len(all_targets) == 1:
            targets = all_targets
            kind_normalized = targets[0].kind
        else:
            sorted_targets = sorted(all_targets, key=lambda t: (t.kind, t.display_name))

            label_to_target: dict[str, AssessmentTarget] = {}
            for target in sorted_targets:
                label = f"[{target.kind}] {target.display_name}"
                label_to_target[label] = target

            selection = questionary.select(
                "Select target",
                choices=list(label_to_target.keys()),
            ).ask()
            if selection is None:
                raise typer.Exit(1)

            selected = label_to_target.get(selection)
            if selected is None:
                console.print("[red]Invalid selection![/red]")
                raise typer.Exit(1)

            targets = [selected]
            kind_normalized = selected.kind
    else:
        if not project_path.exists():
            console.print(f"[red]Error: {project_path} does not exist[/red]")
            raise typer.Exit(1)

        if not project_path.is_dir():
            console.print(f"[red]Error: {project_path} must be a directory[/red]")
            raise typer.Exit(1)

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
        if kind_normalized is None:
            console.print(
                "[red]Error: Could not derive assessment type from path. "
                "Expected folder name: katas, mcp_katas, rag, or capstone.[/red]"
            )
            raise typer.Exit(1)

    if targets is not None:
        if kind_normalized in {"rag", "capstone"} and len(targets) == 1:
            selected_path = _select_project_folder(targets[0].target_path, kind_normalized)
            targets = [
                AssessmentTarget(
                    kind=kind_normalized,
                    target_path=selected_path,
                    base_path=selected_path,
                    display_name=selected_path.name,
                    relative_file=None,
                )
            ]
        _run_targets(targets, output_dir, output)
        return

    if kind_normalized in {"agent", "mcp"}:
        target_root = project_path if project_path is not None else Path.cwd()
        all_targets = _resolve_assessment_targets(target_root)
        if not all_targets:
            console.print(f"[red]No {kind_normalized} targets found in {target_root}[/red]")
            raise typer.Exit(1)

        if project_path is not None and len(all_targets) == 1:
            targets = all_targets
        else:
            selected = _select_assessment_target(all_targets, kind_normalized)
            targets = [selected]
    else:
        if project_path is None:
            path_input = questionary.text("Enter project path").ask()
            if not path_input:
                raise typer.Exit(1)
            project_path = Path(path_input)

        selected_path = _select_project_folder(project_path, kind_normalized)
        targets = [
            AssessmentTarget(
                kind=kind_normalized,
                target_path=selected_path,
                base_path=selected_path,
                display_name=selected_path.name,
                relative_file=None,
            )
        ]

    _run_targets(targets, output_dir, output)


@app.command()
def info():
    """
    Display information about the Capstone Assessor and assessment criteria.
    
    Shows what the agent checks for and the six assessment categories used
    to evaluate capstone projects in the AI Engineering Upskilling Program.
    """
    console.print("\n[bold cyan]Capstone Assessor[/bold cyan]")
    console.print("AI-powered assessment tool for capstone projects\n")
    console.print("The agent will explore your codebase using tools to:")
    console.print("  • Search for Pydantic AI usage (REQUIRED)")
    console.print("  • Find multi-agent architecture")
    console.print("  • Verify RAG implementation")
    console.print("  • Check memory systems")
    console.print("  • Validate guardrails")
    console.print("  • Confirm OTEL observability")
    console.print("  • Review evaluation framework\n")
    console.print("Assessment Categories:")
    console.print("  1. System Architecture & Design")
    console.print("  2. Implementation & Functionality")
    console.print("  3. Evaluation & Metrics")
    console.print("  4. Code Quality & Engineering Practices")
    console.print("  5. Documentation & User Experience")
    console.print("  6. Innovation & Initiative (Bonus)\n")


@app.command()
def bulk_assess(
    base_path: Path = typer.Argument(
        ..., 
        help="Path to directory containing multiple student project directories"
    ),
    output_dir: Path = typer.Option(
        None,
        "--output-dir",
        "-o",
        help="Directory for HTML reports (defaults to saving in each project dir)",
    ),
):
    """
    Assess multiple capstone projects in batch mode.
    
    Processes all subdirectories in the base path as separate projects.
    For each project:
    - Generates an HTML assessment report
    - Saves JSON data file in the project directory
    - Displays summary table with ratings and scores
    
    HTML reports can be saved to a central location or within each project.
    JSON files are always saved in each project as 'capstone_assessment.json'.
    
    Example:
        capstone-assessor bulk-assess ~/students/capstones
        capstone-assessor bulk-assess ~/students/capstones -o ~/reports
    """
    if not base_path.exists():
        console.print(f"[red]Error: {base_path} does not exist[/red]")
        raise typer.Exit(1)

    if not base_path.is_dir():
        console.print(f"[red]Error: {base_path} must be a directory[/red]")
        raise typer.Exit(1)

    project_dirs = [
        p for p in base_path.iterdir() if p.is_dir() and not p.name.startswith(".")
    ]

    if not project_dirs:
        console.print(f"[red]Error: No project directories found in {base_path}[/red]")
        raise typer.Exit(1)

    console.print(
        f"\n[bold cyan]Found {len(project_dirs)} projects to assess[/bold cyan]\n"
    )

    results: list[dict[str, str]] = []

    for i, project_path in enumerate(project_dirs, 1):
        project_name = project_path.name
        console.print(
            f"[bold cyan][{i}/{len(project_dirs)}] Assessing:[/bold cyan] {project_name}"
        )
        console.print(f"[dim]Source: {project_path}[/dim]\n")

        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
            ) as progress:
                task = progress.add_task(
                    "Agent exploring codebase and running assessment...", total=None
                )

                result = assessment_agent.run_sync(
                    "Thoroughly assess this capstone project. Use your tools to explore the codebase systematically and gather evidence for each rubric category. Be thorough in checking for all required components.",
                    deps=project_path,
                )

                progress.update(task, completed=True)

            assessment = result.output
            html_content = generate_html_report(assessment, project_name)

            if output_dir:
                output_dir.mkdir(parents=True, exist_ok=True)
                output_path = output_dir / f"{project_name}_assessment.html"
            else:
                output_path = project_path / "capstone_assessment.html"

            output_path.write_text(html_content)

            json_path = project_path / "capstone_assessment.json"
            json_data = assessment.model_dump(mode="json")
            json_data.pop("overall_score", None)
            json_path.write_text(json.dumps(json_data, indent=2))

            console.print("[bold green]✓[/bold green] Assessment complete!")
            console.print(f"[bold]Overall Rating:[/bold] {assessment.overall_rating}")
            # console.print(f"[bold]Overall Score:[/bold] {assessment.overall_score}/100")
            console.print(f"[cyan]Report saved to:[/cyan] {output_path.absolute()}\n")

            results.append(
                {
                    "name": project_name,
                    "rating": assessment.overall_rating.value,
                    # "score": assessment.overall_score,
                    "path": str(output_path.absolute()),
                }
            )

        except Exception as e:
            console.print(
                f"[bold red]✗[/bold red] Failed to assess {project_name}: {e}\n"
            )
            results.append(
                {"name": project_name, "rating": "ERROR", "path": "N/A"}
            )

    console.print("\n[bold cyan]Bulk Assessment Summary[/bold cyan]\n")

    table = Table(show_header=True, header_style="bold cyan")
    table.add_column("Project", style="bold")
    table.add_column("Rating", justify="center")
    # table.add_column("Score", justify="right")

    for r in results:
        rating_color = (
            "green"
            if r["rating"] in ["Excellent", "Good"]
            else "yellow"
            if r["rating"] in ["Satisfactory"]
            else "red"
        )
        table.add_row(
            r["name"],
            f"[{rating_color}]{r['rating']}[/{rating_color}]",
            #f"{r['score']}/100",
        )

    console.print(table)
    console.print()


@app.command()
def commit_assessments(
    base_path: Path = typer.Argument(
        ..., help="Path to directory containing student projects"
    ),
    message: str = typer.Option(
        "Add capstone assessment", "--message", "-m", help="Git commit message"
    ),
    push: bool = typer.Option(
        True, "--push/--no-push", help="Push to remote after commit"
    ),
):
    """
    Commit and push assessment files to student project repositories.
    
    For each project directory:
    - Stages capstone_assessment.html and capstone_assessment.json
    - Creates a git commit with the specified message
    - Optionally pushes to the remote repository
    
    Useful after running bulk-assess to distribute assessment results
    back to student repositories.
    
    Example:
        capstone-assessor commit-assessments ~/students/capstones
        capstone-assessor commit-assessments ~/students/capstones -m "Final assessment" --no-push
    """
    if not base_path.exists():
        console.print(f"[red]Error: {base_path} does not exist[/red]")
        raise typer.Exit(1)

    if not base_path.is_dir():
        console.print(f"[red]Error: {base_path} must be a directory[/red]")
        raise typer.Exit(1)

    project_dirs = [
        p for p in base_path.iterdir() if p.is_dir() and not p.name.startswith(".")
    ]

    if not project_dirs:
        console.print(f"[red]Error: No project directories found in {base_path}[/red]")
        raise typer.Exit(1)

    console.print(
        f"\n[bold cyan]Committing assessments in {len(project_dirs)} projects[/bold cyan]\n"
    )

    for i, project_path in enumerate(project_dirs, 1):
        project_name = project_path.name
        console.print(
            f"[bold cyan][{i}/{len(project_dirs)}][/bold cyan] {project_name}"
        )

        assessment_files = ["capstone_assessment.html", "capstone_assessment.json"]

        files_exist = [f for f in assessment_files if (project_path / f).exists()]

        if not files_exist:
            console.print("  [yellow]⊘ No assessment files found[/yellow]\n")
            continue

        try:
            subprocess.run(
                ["git", "add"] + files_exist,
                cwd=project_path,
                check=True,
                capture_output=True,
            )

            result = subprocess.run(
                ["git", "commit", "-m", message],
                cwd=project_path,
                capture_output=True,
                text=True,
            )

            if result.returncode == 0:
                console.print(f"  [green]✓ Committed: {', '.join(files_exist)}[/green]")

                if push:
                    push_result = subprocess.run(
                        ["git", "push"],
                        cwd=project_path,
                        capture_output=True,
                        text=True,
                    )

                    if push_result.returncode == 0:
                        console.print("  [green]✓ Pushed to remote[/green]")
                    else:
                        console.print(
                            f"  [yellow]⊘ Push failed: {push_result.stderr.strip()}[/yellow]"
                        )
            else:
                if (
                    "nothing to commit" in result.stdout
                    or "nothing to commit" in result.stderr
                ):
                    console.print("  [dim]⊘ Nothing to commit[/dim]")
                else:
                    console.print(
                        f"  [yellow]⊘ Commit failed: {result.stderr.strip()}[/yellow]"
                    )

        except subprocess.CalledProcessError as e:
            console.print(
                f"  [red]✗ Git error: {e.stderr.decode() if e.stderr else str(e)}[/red]"
            )
        except Exception as e:
            console.print(f"  [red]✗ Error: {e}[/red]")

        console.print()

    console.print("[bold green]Done![/bold green]\n")


if __name__ == "__main__":
    app()
