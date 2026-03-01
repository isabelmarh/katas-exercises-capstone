def run_ruff(target: str = ".", fix: bool = False, format_code: bool = False):
    """
    Runs Ruff to lint and optionally format Python code.
    
    Args:
        target: The file or directory to check (default is current directory ".").
        fix: If True, Ruff will attempt to automatically fix lint errors (`ruff check --fix`).
        format_code: If True, Ruff will also format the code (`ruff format`).
    """
    import subprocess
    
    results = []
    
    if format_code:
        fmt_cmd = ["ruff", "format", target]
        try:
            fmt_res = subprocess.run(fmt_cmd, capture_output=True, text=True)
            results.append("--- Ruff Format ---\n" + (fmt_res.stdout or fmt_res.stderr or "Already formatted."))
        except Exception as e:
            results.append(f"Error running ruff format: {str(e)}")

    lint_cmd = ["ruff", "check", target]
    if fix:
        lint_cmd.append("--fix")
    
    try:
        lint_res = subprocess.run(lint_cmd, capture_output=True, text=True)
        results.append("--- Ruff Check (Lint) ---\n" + (lint_res.stdout or lint_res.stderr or "No lint issues found!"))
    except Exception as e:
        results.append(f"Error running ruff check: {str(e)}")
        
    return "\n\n".join(results)
