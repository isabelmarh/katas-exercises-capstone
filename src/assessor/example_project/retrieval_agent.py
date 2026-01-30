from pydantic_ai import Agent
from pydantic import BaseModel
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer
from opentelemetry import trace

tracer = trace.get_tracer(__name__)


class RetrievalResult(BaseModel):
    documents: list[str]
    scores: list[float]
    query: str


class RAGContext(BaseModel):
    qdrant_client: QdrantClient
    encoder: SentenceTransformer


retrieval_agent = Agent(
    "anthropic:claude-sonnet-4-20250514",
    deps_type=RAGContext,
)


@tracer.start_as_current_span("retrieve_documents")
async def retrieve_documents(
    ctx: RAGContext, query: str, top_k: int = 5
) -> RetrievalResult:
    query_vector = ctx.encoder.encode(query).tolist()

    results = ctx.qdrant_client.search(
        collection_name="documentation",
        query_vector=query_vector,
        limit=top_k,
        with_payload=True,
    )

    documents = [hit.payload["text"] for hit in results]
    scores = [hit.score for hit in results]

    return RetrievalResult(documents=documents, scores=scores, query=query)
