import asyncio
from pathlib import Path
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import ConsoleSpanExporter, BatchSpanProcessor

from router_agent import route_query
from retrieval_agent import retrieve_documents, RAGContext
from synthesis_agent import synthesize_response
from memory_agent import MemoryAgent
from guardrails import InputGuardrails


trace.set_tracer_provider(TracerProvider())
trace.get_tracer_provider().add_span_processor(
    BatchSpanProcessor(ConsoleSpanExporter())
)

tracer = trace.get_tracer(__name__)


class MultiAgentRAGSystem:
    def __init__(self):
        self.qdrant = QdrantClient(path="./qdrant_data")
        self.encoder = SentenceTransformer("all-MiniLM-L6-v2")
        self.memory = MemoryAgent(Path("memory.db"))
        self.guardrails = InputGuardrails()
        self.user_id = "default_user"

    @tracer.start_as_current_span("process_query")
    async def process_query(self, query: str) -> str:
        guardrail_result = self.guardrails.validate_input(query)
        if not guardrail_result.passed:
            return f"Input validation failed: {guardrail_result.reason}"

        sanitized_query = guardrail_result.sanitized_input

        route = await route_query(sanitized_query)

        history = self.memory.get_history(self.user_id)

        if route.route == "retrieval":
            rag_context = RAGContext(qdrant_client=self.qdrant, encoder=self.encoder)
            retrieval_result = await retrieve_documents(rag_context, sanitized_query)
            response = await synthesize_response(
                sanitized_query, retrieval_result.documents, history
            )
        else:
            response = f"Direct response for: {sanitized_query}"

        self.memory.store_message(self.user_id, "user", sanitized_query)
        self.memory.store_message(self.user_id, "assistant", response)

        return response


async def main():
    system = MultiAgentRAGSystem()

    query = "How do I implement async agents in Pydantic AI?"
    print(f"Query: {query}\n")

    response = await system.process_query(query)
    print(f"Response: {response}")


if __name__ == "__main__":
    asyncio.run(main())
