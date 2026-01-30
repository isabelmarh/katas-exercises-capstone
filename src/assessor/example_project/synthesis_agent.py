from pydantic_ai import Agent
from pydantic import BaseModel
from opentelemetry import trace

tracer = trace.get_tracer(__name__)


class SynthesisInput(BaseModel):
    query: str
    context: list[str]
    conversation_history: list[dict[str, str]]


synthesis_agent = Agent(
    "anthropic:claude-sonnet-4-20250514",
    system_prompt="""You synthesize responses using retrieved context and conversation history.
    
    Guidelines:
    - Answer based on provided context
    - Be accurate and cite sources when possible
    - Maintain conversation flow
    - If context doesn't contain answer, say so clearly
    """,
)


@tracer.start_as_current_span("synthesize_response")
async def synthesize_response(
    query: str, context: list[str], history: list[dict]
) -> str:
    context_str = "\n\n".join([f"[Doc {i + 1}] {doc}" for i, doc in enumerate(context)])
    history_str = "\n".join([f"{m['role']}: {m['content']}" for m in history[-3:]])

    prompt = f"""Context:\n{context_str}

Recent conversation:\n{history_str}

User query: {query}

Provide a helpful response based on the context."""

    result = await synthesis_agent.run(prompt)
    return result.data
