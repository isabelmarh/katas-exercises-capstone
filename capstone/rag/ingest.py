from pathlib import Path

from .chunking import chunk_text
from .vector_store import LocalVectorStore


def ingest_directory(data_dir: Path) -> int:
    """Load markdown and text files from disk into the placeholder store."""
    store = LocalVectorStore()
    total_chunks = 0

    for path in sorted(data_dir.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in {".md", ".txt"}:
            continue
        text = path.read_text(encoding="utf-8")
        chunks = chunk_text(text, source=str(path))
        store.upsert(chunks)
        total_chunks += len(chunks)

    return total_chunks


if __name__ == "__main__":
    root = Path(__file__).resolve().parent.parent / "data" / "raw"
    count = ingest_directory(root)
    print(f"Ingested {count} chunks from {root}")
