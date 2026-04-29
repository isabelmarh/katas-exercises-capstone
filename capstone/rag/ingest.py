from pathlib import Path

from .chunking import chunk_text
from .vector_store import LocalVectorStore


def infer_category(path: Path, root: Path) -> str:
    try:
        relative = path.relative_to(root)
    except ValueError:
        return "notes"
    return relative.parts[0] if len(relative.parts) > 1 else "notes"


def ingest_directory(data_dir: Path, index_path: Path) -> int:
    """Load markdown and text files from disk into a local JSON index."""
    store = LocalVectorStore(index_path)
    store._rows = []

    for path in sorted(data_dir.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in {".md", ".txt"}:
            continue
        text = path.read_text(encoding="utf-8")
        relative = path.relative_to(data_dir)
        title = path.stem.replace("_", " ").replace("-", " ").title()
        category = infer_category(path, data_dir)
        chunks = chunk_text(
            text,
            source=str(relative),
            title=title,
            category=category,
        )
        store.upsert(chunks)

    store.save()
    return store.chunk_count()


if __name__ == "__main__":
    root = Path(__file__).resolve().parent.parent / "data" / "raw"
    index = Path(__file__).resolve().parent.parent / "storage" / "career_index.json"
    count = ingest_directory(root, index)
    print(f"Ingested {count} chunks from {root} into {index}")
