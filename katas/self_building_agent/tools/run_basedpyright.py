def run_basedpyright(target: str = "."):
    """
    Runs basedpyright for static type checking on a Python file or directory.
    
    Args:
        target: The file or directory to type check (default is current directory ".").
    """
    import subprocess
    cmd = ["basedpyright", target]
    try:
        # basedpyright might return non-zero if there are type errors, so we don't use check=True
        result = subprocess.run(cmd, capture_output=True, text=True)
        output = result.stdout if result.stdout else result.stderr
        return output if output else "basedpyright finished with no output."
    except Exception as e:
        return f"Error running basedpyright: {str(e)}"
