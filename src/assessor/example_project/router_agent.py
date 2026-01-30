from pydantic_ai import Agent
from pydantic import BaseModel
from opentelemetry import trace

tracer = trace.get_tracer(__name__)


class QueryRoute(BaseModel):
    route: str
    confidence: float
    reasoning: str


router_agent = Agent(
    "anthropic:claude-sonnet-4-20250514",
    result_type=QueryRoute,
    system_prompt="""You are a routing agent that determines how to handle user queries.
    
    Routes:
    - 'retrieval': Query needs document search (technical questions, how-to)
    - 'direct': Simple query that can be answered without retrieval (greetings, status)
    - 'memory': Query about past conversation or user preferences
    """,
)


@tracer.start_as_current_span("route_query")
async def route_query(query: str) -> QueryRoute:
    result = await router_agent.run(f"Route this query: {query}")
    return result.data
