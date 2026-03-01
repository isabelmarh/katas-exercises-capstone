def rg_find_replace(directory: str, pattern: str, replacement: str, is_regex: bool = False, file_glob: str = None) -> str:
    """
    Finds and replaces text across files in a directory using ripgrep to quickly locate candidates.
    
    Args:
        directory: The directory to search in.
        pattern: The string or regular expression to search for.
        replacement: The string to replace it with.
        is_regex: If True, treats pattern as a regex. If False, treats it as a literal string.
        file_glob: Optional file glob pattern (e.g., '*.py') to filter files.
    """
    import subprocess
    import re

    # Construct the ripgrep command to just list matching files
    cmd = ["rg", "-l"]
    if not is_regex:
        cmd.append("-F")
    if file_glob:
        cmd.extend(["-g", file_glob])
    
    cmd.extend([pattern, directory])

    try:
        # Run ripgrep
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=False)
        
        # ripgrep returns 1 if no matches are found, 0 if matches are found. 
        # >1 means an error occurred.
        if result.returncode > 1:
            return f"Error running ripgrep: {result.stderr}"
        
        files_to_process = [f for f in result.stdout.splitlines() if f.strip()]
        
        if not files_to_process:
            return "No matching files found."

        modified_files = []
        for filepath in files_to_process:
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                if is_regex:
                    # using Python's re engine for replacement
                    new_content, count = re.subn(pattern, replacement, content)
                else:
                    count = content.count(pattern)
                    new_content = content.replace(pattern, replacement)

                if count > 0:
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    modified_files.append(f"{filepath} ({count} replacements)")
            except Exception as e:
                # skip files that can't be decoded as UTF-8
                pass
        
        if not modified_files:
            return "Found files, but no replacements were made (possibly due to regex engine differences or encoding issues)."
            
        return f"Successfully modified {len(modified_files)} files:\n" + "\n".join(modified_files)

    except Exception as e:
        return f"Unexpected error: {str(e)}"
