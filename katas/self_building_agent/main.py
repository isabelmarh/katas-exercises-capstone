import subprocess
from difflib import SequenceMatcher
from pathlib import Path
from typing import get_args, Any, Callable

from pydantic_ai.models.google import LatestGoogleModelNames
from pydantic_ai import Agent, FunctionToolset, RunContext

TOOLS_DIR = Path(__file__).parent / "tools"
TOOLS_DIR.mkdir(exist_ok=True)


def make_toolset(ctx: RunContext) -> FunctionToolset:
    toolset = FunctionToolset()
    loaded: set[str] = set()

    @toolset.tool
    def read_file(path: str) -> str:
        """Read a file from disk."""
        try:
            return Path(path).read_text()
        except Exception as e:
            return f"Error: {e}"

    @toolset.tool
    def write_file(path: str, content: str) -> str:
        """Write content to a file."""
        try:
            p = Path(path)
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(content)
            return f"Written {p}"
        except Exception as e:
            return f"Error: {e}"

    @toolset.tool
    def edit_file(path: str, old_str: str, new_str: str) -> str:
        """Replace old_str with new_str in a file. Must match exactly once."""
        try:
            p = Path(path)
            text = p.read_text()
            if text.count(old_str) != 1:
                return f"Error: expected 1 match, found {text.count(old_str)}"
            p.write_text(text.replace(old_str, new_str, 1))
            return f"Edited {p}"
        except Exception as e:
            return f"Error: {e}"

    @toolset.tool
    def bash(command: str) -> str:
        """Run a bash command and return stdout + stderr."""
        try:
            r = subprocess.run(
                command, shell=True, capture_output=True, text=True, timeout=30
            )
            return (r.stdout + r.stderr).strip()
        except Exception as e:
            return f"Error: {e}"

    @toolset.tool
    def search_tools(query: str = "") -> list[dict[str, str]]:
        """Fuzzy search saved tools, auto-loads top 3 matches. Use create_tool if nothing fits."""
        scored: list[tuple[float, str, str, Callable[..., Any]]] = []
        for path in TOOLS_DIR.glob("*.py"):
            if path.stem in loaded:
                continue
            try:
                ns: dict[str, Any] = {}
                exec(path.read_text(), ns)
                fn: Callable[..., Any] = ns[path.stem]
                doc: str = (fn.__doc__ or "").strip()
                score: float = (
                    SequenceMatcher(
                        None, query.lower(), f"{path.stem} {doc}".lower()
                    ).ratio()
                    if query
                    else 1.0
                )
                scored.append((score, path.stem, doc, fn))
            except Exception:
                pass
        top3 = sorted(scored, key=lambda x: x[0], reverse=True)[:3]
        for _, name, _, fn in top3:
            toolset.add_function(fn)
            loaded.add(name)
        return [{"name": n, "description": d} for _, n, d, _ in top3]

    @toolset.tool
    def create_tool(name: str, code: str) -> str:
        """Write and immediately register a new tool. code must define a function named `name` with a docstring."""
        try:
            ns: dict[str, Any] = {}
            exec(code, ns)
            fn: Callable[..., Any] = ns[name]
            toolset.add_function(fn)
            loaded.add(name)
            (TOOLS_DIR / f"{name}.py").write_text(code)
            return f"Created and loaded: {name}"
        except Exception as e:
            return f"Error: {e}"

    _ = (read_file, write_file, edit_file, bash, search_tools, create_tool)

    return toolset


agent = Agent(
    model="google-gla:gemini-2.5-pro",
    instructions=(
        "You have read_file, write_file, edit_file, bash, search_tools, and create_tool. "
        "Always search_tools first — top 3 matches are auto-loaded and ready to call. "
        "Avoid using the bash tool if a specific tool exists or can be created. "
        "Only use create_tool if nothing fits."
    ),
    toolsets=[make_toolset],
)
models = list(get_args(LatestGoogleModelNames))
app = agent.to_web(models=models)
