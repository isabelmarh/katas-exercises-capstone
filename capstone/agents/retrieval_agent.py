from pathlib import Path

from pydantic import BaseModel

try:
    from ..rag.vector_store import LocalVectorStore
except ImportError:
    from rag.vector_store import LocalVectorStore


class RetrievalResult(BaseModel):
    documents: list[str]
    scores: list[float]
    query: str
    sources: list[str]
    categories: list[str]


def retrieve_documents(query: str, top_k: int = 5) -> RetrievalResult:
    """Retrieve semantically similar chunks from the local career index."""
    index_path = Path(__file__).resolve().parent.parent / "storage" / "career_index.json"
    store = LocalVectorStore(index_path)
    ranked = store.search(query, top_k=top_k)
    return RetrievalResult(
        documents=[chunk.text for chunk, _score in ranked],
        scores=[round(score, 3) for _chunk, score in ranked],
        query=query,
        sources=[chunk.source for chunk, _score in ranked],
        categories=[chunk.category for chunk, _score in ranked],
    )
