from pydantic import BaseModel


class QueryRoute(BaseModel):
    route: str
    confidence: float
    reasoning: str


def route_query(query: str) -> QueryRoute:
    """Temporary deterministic router stub for early development."""
    lowered = query.lower()
    if "remember" in lowered or "preference" in lowered:
        return QueryRoute(route="memory", confidence=0.7, reasoning="memory keyword")
    if "why" in lowered or "what role" in lowered or "skills" in lowered:
        return QueryRoute(route="retrieval", confidence=0.8, reasoning="career query")
    return QueryRoute(route="direct", confidence=0.5, reasoning="default route")
