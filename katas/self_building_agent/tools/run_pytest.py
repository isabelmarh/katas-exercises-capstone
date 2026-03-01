def run_pytest(target: str = ".", test_file: str = None, keyword: str = None):
    """
    Runs pytest on the project, a specific file, or specific test cases.
    
    Args:
        target: Directory containing the tests (default: '.').
        test_file: Specific test file to run (optional).
        keyword: Only run tests matching this keyword/expression (optional, passed to pytest -k).
    """
    import subprocess
    cmd = ["pytest"]
    if test_file:
        cmd.append(test_file)
    else:
        cmd.append(target)
        
    if keyword:
        cmd.extend(["-k", keyword])
        
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        output = result.stdout if result.stdout else result.stderr
        return output if output else "pytest finished with no output."
    except Exception as e:
        return f"Error running pytest: {str(e)}"
