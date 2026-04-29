import json
from pathlib import Path
from typing import Any

from .chunking import DocumentChunk
from .embeddings import cosine_similarity, term_frequencies


class LocalVectorStore:
    """JSON-backed local search index using bag-of-words similarity."""

    def __init__(self, index_path: Path) -> None:
        self.index_path = index_path
        self._rows: list[dict[str, Any]] = []
        if self.index_path.exists():
            self._rows = json.loads(self.index_path.read_text(encoding="utf-8"))

    def upsert(self, chunks: list[DocumentChunk]) -> None:
        for chunk in chunks:
            row = chunk.to_dict()
            row["term_frequencies"] = dict(term_frequencies(chunk.text))
            self._rows.append(row)

    def save(self) -> None:
        self.index_path.parent.mkdir(parents=True, exist_ok=True)
        self.index_path.write_text(
            json.dumps(self._rows, indent=2, ensure_ascii=True),
            encoding="utf-8",
        )

    def chunk_count(self) -> int:
        return len(self._rows)

    def search(self, query: str, top_k: int = 5) -> list[tuple[DocumentChunk, float]]:
        query_terms = term_frequencies(query)
        ranked: list[tuple[DocumentChunk, float]] = []

        for row in self._rows:
            score = cosine_similarity(
                query_terms,
                term_frequencies(" ".join([row["title"], row["category"], row["text"]])),
            )
            if score <= 0.0:
                continue
            ranked.append(
                (
                    DocumentChunk(
                        source=row["source"],
                        title=row["title"],
                        category=row["category"],
                        text=row["text"],
                        chunk_id=row["chunk_id"],
                    ),
                    score,
                )
            )

        ranked.sort(key=lambda item: item[1], reverse=True)
        return ranked[:top_k]
