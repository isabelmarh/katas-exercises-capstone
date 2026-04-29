from dataclasses import asdict, dataclass


@dataclass
class DocumentChunk:
    source: str
    title: str
    category: str
    text: str
    chunk_id: str

    def to_dict(self) -> dict[str, str]:
        return asdict(self)


def chunk_text(
    text: str,
    source: str,
    title: str,
    category: str,
    chunk_size: int = 500,
    overlap: int = 80,
) -> list[DocumentChunk]:
    """Split text into overlapping fixed-size chunks for lightweight local retrieval."""
    normalized = text.strip()
    if not normalized:
        return []
    chunks: list[DocumentChunk] = []
    start = 0
    index = 0
    step = max(1, chunk_size - overlap)

    while start < len(normalized):
        end = start + chunk_size
        current_text = normalized[start:end].strip()
        if current_text:
            chunks.append(
                DocumentChunk(
                    source=source,
                    title=title,
                    category=category,
                    text=current_text,
                    chunk_id=f"{source}::chunk-{index}",
                )
            )
            index += 1
        start += step

    return chunks
