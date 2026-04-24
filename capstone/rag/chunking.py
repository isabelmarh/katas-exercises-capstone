from dataclasses import dataclass


@dataclass
class DocumentChunk:
    source: str
    text: str


def chunk_text(text: str, source: str, chunk_size: int = 500) -> list[DocumentChunk]:
    """Split text into fixed-size chunks as a simple MVP."""
    normalized = text.strip()
    if not normalized:
        return []
    return [
        DocumentChunk(source=source, text=normalized[i : i + chunk_size])
        for i in range(0, len(normalized), chunk_size)
    ]
