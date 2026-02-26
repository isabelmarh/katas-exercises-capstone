from pathlib import Path


def _find_nested_readme_dir(project_path: Path) -> Path | None:
    """Return the sole child directory that contains a README, if unique."""
    candidates: list[Path] = []
    for child in project_path.iterdir():
        if not child.is_dir() or child.name.startswith("."):
            continue
        if any(
            (child / name).exists()
            for name in ["README.md", "README.txt", "readme.md", "README.rst"]
        ):
            candidates.append(child)
    if len(candidates) == 1:
        return candidates[0]
    return None


def search_code_content(
    project_path: Path, pattern: str, file_extension: str = ".py"
) -> list[dict[str, str]]:
    """Search for pattern in code files and return matches with context."""
    results = []
    files = list(project_path.rglob(f"*{file_extension}"))
    files = [
        f
        for f in files
        if not any(part.startswith(".") for part in f.parts)
        and "__pycache__" not in str(f)
    ]

    for file in files[:100]:
        try:
            content = file.read_text()
            if pattern.lower() in content.lower():
                lines = content.splitlines()
                matching_lines = [
                    (i, line)
                    for i, line in enumerate(lines)
                    if pattern.lower() in line.lower()
                ]

                if matching_lines:
                    results.append(
                        {
                            "file": str(file.relative_to(project_path)),
                            "matches": len(matching_lines),
                            "sample_lines": [
                                f"Line {i + 1}: {line.strip()}"
                                for i, line in matching_lines[:3]
                            ],
                        }
                    )
        except Exception:
            pass

    return results


def list_python_files(project_path: Path) -> list[str]:
    """List all Python files in the project."""
    files = list(project_path.rglob("*.py"))
    files = [
        f
        for f in files
        if not any(part.startswith(".") for part in f.parts)
        and "__pycache__" not in str(f)
    ]
    return [str(f.relative_to(project_path)) for f in sorted(files)]


def read_file_content(
    project_path: Path, relative_path: str, max_lines: int = 200
) -> str:
    """Read content of a specific file."""
    try:
        file_path = project_path / relative_path
        if not file_path.exists() or not file_path.is_file():
            return f"File not found: {relative_path}"

        content = file_path.read_text()
        lines = content.splitlines()

        if len(lines) > max_lines:
            return (
                "\n".join(lines[:max_lines])
                + f"\n\n... (truncated, showing first {max_lines} of {len(lines)} lines)"
            )
        return content
    except Exception as e:
        return f"Error reading file: {e}"


def get_project_structure(project_path: Path) -> dict[str, any]:
    """Get high-level project structure."""
    structure = {
        "directories": [],
        "python_files_count": 0,
        "test_files_count": 0,
        "has_readme": False,
        "has_pyproject": False,
        "has_requirements": False,
        "config_files": [],
    }

    dirs = [
        d.name
        for d in project_path.iterdir()
        if d.is_dir() and not d.name.startswith(".")
    ]
    structure["directories"] = sorted(dirs)

    py_files = list(project_path.rglob("*.py"))
    py_files = [f for f in py_files if "__pycache__" not in str(f)]
    structure["python_files_count"] = len(py_files)

    test_files = [f for f in py_files if "test" in f.name.lower()]
    structure["test_files_count"] = len(test_files)

    structure["has_readme"] = any(
        (project_path / name).exists()
        for name in ["README.md", "README.txt", "readme.md"]
    )
    if not structure["has_readme"]:
        structure["has_readme"] = _find_nested_readme_dir(project_path) is not None
    structure["has_pyproject"] = (project_path / "pyproject.toml").exists()
    structure["has_requirements"] = (project_path / "requirements.txt").exists()

    config_patterns = ["*.toml", "*.yaml", "*.yml", "*.json", ".env.example"]
    for pattern in config_patterns:
        config_files = list(project_path.glob(pattern))
        structure["config_files"].extend([f.name for f in config_files if f.is_file()])

    return structure


def read_dependencies(project_path: Path) -> str:
    """Read project dependencies."""
    deps = []

    pyproject = project_path / "pyproject.toml"
    if pyproject.exists():
        deps.append(f"=== pyproject.toml ===\n{pyproject.read_text()}")

    requirements = project_path / "requirements.txt"
    if requirements.exists():
        deps.append(f"=== requirements.txt ===\n{requirements.read_text()}")

    return "\n\n".join(deps) if deps else "No dependency files found"


def read_readme(project_path: Path) -> str:
    """Read README file."""
    for name in ["README.md", "README.txt", "readme.md", "README.rst"]:
        readme = project_path / name
        if readme.exists():
            return readme.read_text()
    nested_dir = _find_nested_readme_dir(project_path)
    if nested_dir:
        for name in ["README.md", "README.txt", "readme.md", "README.rst"]:
            readme = nested_dir / name
            if readme.exists():
                return readme.read_text()
    return "No README found"
