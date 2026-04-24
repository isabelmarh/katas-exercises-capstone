from .chunking import DocumentChunk


class LocalVectorStore:
    """In-memory placeholder until a real local vector DB is wired in."""

    def __init__(self) -> None:
        self._chunks: list[DocumentChunk] = []

    def upsert(self, chunks: list[DocumentChunk]) -> None:
        self._chunks.extend(chunks)

    def search(self, query: str, top_k: int = 5) -> list[DocumentChunk]:
        return self._chunks[:top_k]
