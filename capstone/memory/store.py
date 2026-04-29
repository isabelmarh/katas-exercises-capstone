import sqlite3
from pathlib import Path


class MemoryStore:
    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path
        self._init_db()

    def _init_db(self) -> None:
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS conversations (
                    id INTEGER PRIMARY KEY,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS preferences (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS episodic_memories (
                    id INTEGER PRIMARY KEY,
                    summary TEXT NOT NULL,
                    tags TEXT NOT NULL,
                    relevance_score REAL NOT NULL DEFAULT 0.5,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    last_accessed TEXT DEFAULT CURRENT_TIMESTAMP
                )
                """
            )

    def save_message(self, role: str, content: str) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT INTO conversations (role, content) VALUES (?, ?)",
                (role, content),
            )

    def get_recent_messages(self, limit: int = 10) -> list[tuple[str, str]]:
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute(
                "SELECT role, content FROM conversations ORDER BY id DESC LIMIT ?",
                (limit,),
            ).fetchall()
        return list(reversed(rows))

    def save_preference(self, key: str, value: str) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT INTO preferences (key, value, updated_at)
                VALUES (?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(key) DO UPDATE SET
                    value = excluded.value,
                    updated_at = CURRENT_TIMESTAMP
                """,
                (key, value),
            )

    def get_preferences(self) -> dict[str, str]:
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute(
                "SELECT key, value FROM preferences ORDER BY key ASC"
            ).fetchall()
        return {key: value for key, value in rows}

    def save_episode(
        self, summary: str, tags: list[str], relevance_score: float = 0.5
    ) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT INTO episodic_memories (summary, tags, relevance_score)
                VALUES (?, ?, ?)
                """,
                (summary, ",".join(sorted(set(tags))), relevance_score),
            )

    def get_relevant_episodes(
        self, topic_terms: list[str], limit: int = 5
    ) -> list[dict[str, str | float]]:
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute(
                """
                SELECT id, summary, tags, relevance_score
                FROM episodic_memories
                ORDER BY relevance_score DESC, last_accessed DESC
                """
            ).fetchall()

            lowered_terms = {term.lower() for term in topic_terms}
            selected_rows: list[tuple[int, str, str, float]] = []
            for row in rows:
                tags = row[2].lower()
                summary = row[1].lower()
                if not lowered_terms or any(
                    term in tags or term in summary for term in lowered_terms
                ):
                    selected_rows.append(row)

            selected_rows = selected_rows[:limit]
            for row in selected_rows:
                conn.execute(
                    """
                    UPDATE episodic_memories
                    SET last_accessed = CURRENT_TIMESTAMP
                    WHERE id = ?
                    """,
                    (row[0],),
                )

        return [
            {
                "summary": row[1],
                "tags": row[2],
                "relevance_score": row[3],
            }
            for row in selected_rows
        ]

    def reset(self) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM conversations")
            conn.execute("DELETE FROM preferences")
            conn.execute("DELETE FROM episodic_memories")
