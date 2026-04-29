from __future__ import annotations

import json
from pathlib import Path

from mcp.server.fastmcp import FastMCP

try:
    from .app import run_query_with_metadata
    from .agents.memory_agent import get_memory_store
    from .agents.retrieval_agent import retrieve_documents
    from .agents.trajectory_agent import generate_trajectory_plan
    from .rag.ingest import ingest_directory
except ImportError:
    from app import run_query_with_metadata
    from agents.memory_agent import get_memory_store
    from agents.retrieval_agent import retrieve_documents
    from agents.trajectory_agent import generate_trajectory_plan
    from rag.ingest import ingest_directory


mcp = FastMCP("career-compass")


def _ensure_index_exists() -> Path:
    root = Path(__file__).resolve().parent
    data_dir = root / "data" / "raw"
    index_path = root / "storage" / "career_index.json"
    if not index_path.exists():
        ingest_directory(data_dir, index_path)
    return index_path


@mcp.tool()
async def search_career_evidence(query: str, top_k: int = 3) -> str:
    """Search the local second-brain knowledge base for evidence related to a career question.

    Args:
        query: Career question or topic to search for.
        top_k: Number of evidence chunks to return.
    """
    _ensure_index_exists()
    retrieval = retrieve_documents(query, top_k=top_k)
    if not retrieval.documents:
        return "No relevant local evidence found."

    lines = []
    for source, score, document in zip(
        retrieval.sources, retrieval.scores, retrieval.documents
    ):
        lines.append(f"Source: {source} (score={score:.2f})\n{document[:240].strip()}...")
    return "\n\n".join(lines)


@mcp.tool()
async def get_memory_snapshot(topic_hint: str = "") -> str:
    """Inspect semantic and episodic memory for a topic.

    Args:
        topic_hint: Optional topic hint used to filter episodic memories.
    """
    store = get_memory_store()
    preferences = store.get_preferences()
    episodes = store.get_relevant_episodes(topic_hint.lower().split(), limit=5)
    payload = {
        "preferences": preferences,
        "episodic_memories": episodes,
    }
    return json.dumps(payload, indent=2, ensure_ascii=True)


@mcp.tool()
async def build_trajectory_plan(query: str) -> str:
    """Generate a structured career trajectory plan for a target role or growth direction.

    Args:
        query: A role-planning question such as comparing platform vs AI engineering.
    """
    plan = generate_trajectory_plan(query)
    return plan.model_dump_json(indent=2)


@mcp.tool()
async def ask_second_brain(query: str) -> str:
    """Run the full career second-brain orchestration and return the answer plus metadata.

    Args:
        query: User question to send through the full orchestration pipeline.
    """
    execution = run_query_with_metadata(query)
    payload = {
        "route": execution.route,
        "route_reasoning": execution.route_reasoning,
        "retrieved_sources": execution.retrieved_sources,
        "pii_found_in_input": execution.pii_found_in_input,
        "prompt_injection_detected": execution.prompt_injection_detected,
        "response": execution.response,
    }
    return json.dumps(payload, indent=2, ensure_ascii=True)


if __name__ == "__main__":
    mcp.run()
