import sqlite3
from datetime import datetime
from pathlib import Path
from opentelemetry import trace

tracer = trace.get_tracer(__name__)


class MemoryAgent:
    def __init__(self, db_path: Path = Path("memory.db")):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS conversations (
                    id INTEGER PRIMARY KEY,
                    user_id TEXT,
                    role TEXT,
                    content TEXT,
                    timestamp TEXT
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS user_preferences (
                    user_id TEXT PRIMARY KEY,
                    preferences TEXT,
                    updated_at TEXT
                )
            """)

    @tracer.start_as_current_span("store_message")
    def store_message(self, user_id: str, role: str, content: str):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT INTO conversations (user_id, role, content, timestamp) VALUES (?, ?, ?, ?)",
                (user_id, role, content, datetime.now().isoformat()),
            )

    @tracer.start_as_current_span("get_history")
    def get_history(self, user_id: str, limit: int = 10) -> list[dict[str, str]]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT role, content FROM conversations WHERE user_id = ? ORDER BY timestamp DESC LIMIT ?",
                (user_id, limit),
            )
            return [{"role": row[0], "content": row[1]} for row in cursor.fetchall()][
                ::-1
            ]

    @tracer.start_as_current_span("update_preferences")
    def update_preferences(self, user_id: str, preferences: str):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT OR REPLACE INTO user_preferences (user_id, preferences, updated_at) VALUES (?, ?, ?)",
                (user_id, preferences, datetime.now().isoformat()),
            )
