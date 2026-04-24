from pydantic import BaseModel


class RetrievalResult(BaseModel):
    documents: list[str]
    scores: list[float]
    query: str


def retrieve_documents(query: str, top_k: int = 5) -> RetrievalResult:
    """Placeholder retrieval function until vector search is implemented."""
    return RetrievalResult(documents=[], scores=[], query=query)
