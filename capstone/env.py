from __future__ import annotations

import os
from pathlib import Path


def load_local_env() -> Path | None:
    """Load environment variables from capstone/.env if it exists."""
    env_path = Path(__file__).resolve().parent / ".env"
    if not env_path.exists():
        return None

    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        current_value = os.environ.get(key, "").strip()
        if key and not current_value:
            os.environ[key] = value

    return env_path
