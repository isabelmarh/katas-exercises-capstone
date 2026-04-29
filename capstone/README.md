# Career Compass Second Brain

Career Compass Second Brain is a local multi-agent system that helps me decide my next software career step using my own documents, reflections, saved job descriptions, and conversation history.

The project is designed to satisfy the "Second Brain" capstone requirements by combining:

- Pydantic AI for agent orchestration
- Pydantic Evals for evaluation-driven development
- OpenTelemetry for observability
- RAG for semantic retrieval over local career documents
- Persistent memory for conversation history and preferences
- Guardrails to redact PII before saving memory
- A local MCP server for exposing second-brain capabilities as reusable tools

## Goal

Basic chatbots give generic career advice. This project aims to do better by grounding recommendations in my own:

- resume and project history
- saved job descriptions
- learning reflections
- career goals and constraints
- prior conversations and expressed preferences

Example questions:

- What career path fits me best right now?
- What evidence in my notes supports moving toward backend, platform, or AI roles?
- What skills appear most often in target jobs that I do not yet demonstrate strongly?
- What should I do in the next 30 days to move closer to my target role?

## Architecture

The system uses four specialized agents:

1. `Router Agent`
   Decides whether the query needs retrieval, memory lookup, or direct planning.
2. `Retrieval Agent`
   Searches local documents semantically and returns relevant evidence.
3. `Career Coach Agent`
   Synthesizes evidence into grounded, personalized career recommendations.
4. `Memory Agent`
   Stores conversation summaries and user preferences for later reuse.

The current MVP uses real `pydantic_ai.Agent` instances for routing, preference extraction, baseline comparison, and coaching. If a Claude or Gemini API key is available, those agents use a live model. If not, they fall back to a local `FunctionModel` so the workflow remains runnable during development.

Beyond the core agents, the project also includes a structured `Trajectory Agent` that performs skill-gap and career-path planning using Pydantic AI tools plus an output validator.

### Data Flow

```text
User Query
  -> Guardrails
  -> Router Agent
  -> Preference Agent
  -> Retrieval Agent
  -> Trajectory Agent (for roadmap / skill-gap questions)
  -> Career Coach Agent
  -> Output Guardrails
  -> SQLite Memory + User Response
```

The orchestration entry point is [`app.py`](/Users/isabelhong/katas-exercises/katas-exercises/capstone/app.py). The `run_query_with_metadata()` function now returns structured execution metadata showing:

- the selected route
- retrieval sources used
- whether guardrails detected PII
- whether prompt-injection-like text was detected
- whether memory was included in the answer

## Data Sources

Documents are stored locally under [`data/raw/`](/Users/isabelhong/katas-exercises/katas-exercises/capstone/data/raw).

Suggested files:

- `career_journal.md`
- `resume_v1.md`
- `resume_v2.md`
- `job_descriptions/*.md`
- `reflections/*.md`
- `career_goals.md`

## Project Structure

- [`main.py`](/Users/isabelhong/katas-exercises/katas-exercises/capstone/main.py): CLI entry point
- [`app.py`](/Users/isabelhong/katas-exercises/katas-exercises/capstone/app.py): orchestration flow
- [`career_mcp_server.py`](/Users/isabelhong/katas-exercises/katas-exercises/capstone/career_mcp_server.py): local FastMCP server exposing search, memory, trajectory planning, and full orchestration
- [`agents/`](/Users/isabelhong/katas-exercises/katas-exercises/capstone/agents): specialized agents
- [`rag/`](/Users/isabelhong/katas-exercises/katas-exercises/capstone/rag): chunking, embeddings, vector search, ingestion
- [`memory/`](/Users/isabelhong/katas-exercises/katas-exercises/capstone/memory): SQLite memory store and summarization helpers
- [`guardrails.py`](/Users/isabelhong/katas-exercises/katas-exercises/capstone/guardrails.py): PII redaction before persistence
- [`telemetry.py`](/Users/isabelhong/katas-exercises/katas-exercises/capstone/telemetry.py): OTEL setup and tracing spans
- [`evals/`](/Users/isabelhong/katas-exercises/katas-exercises/capstone/evals): datasets and evaluators
- [`IMPLEMENTATION_CHECKLIST.md`](/Users/isabelhong/katas-exercises/katas-exercises/capstone/IMPLEMENTATION_CHECKLIST.md): step-by-step build plan

## Guardrails

The project includes guardrails in [`guardrails.py`](/Users/isabelhong/katas-exercises/katas-exercises/capstone/guardrails.py) for:

- email and phone redaction
- query length limiting
- prompt-injection-like phrase detection
- output sanitization before responses are stored or returned

These guardrails are applied before memory persistence and after model generation.

## Memory Design

The project separates memory into:

- semantic memory: long-lived preferences stored in `preferences`
- episodic memory: interaction summaries with relevance scores stored in `episodic_memories`

This gives the capstone a clearer second-brain architecture than a single flat chat-history table.

## Observability

The project now uses real OpenTelemetry setup in [`telemetry.py`](/Users/isabelhong/katas-exercises/katas-exercises/capstone/telemetry.py).

Observed spans include:

- `save_user_message`
- `route_query`
- `update_preferences`
- `retrieve_documents`
- `generate_response`
- `save_assistant_message`

By default the spans are exported to the console so the capstone has visible OTEL evidence without needing a separate collector during development.

## Innovation Notes

The capstone goes beyond basic agent orchestration in three ways:

- tool-enabled structured planning in [`agents/trajectory_agent.py`](/Users/isabelhong/katas-exercises/katas-exercises/capstone/agents/trajectory_agent.py)
- output validation with a Pydantic AI `output_validator`
- split episodic vs semantic memory with relevance-aware episodic retrieval
- a local FastMCP server in [`career_mcp_server.py`](/Users/isabelhong/katas-exercises/katas-exercises/capstone/career_mcp_server.py) that turns the second brain into reusable tools

## MCP Server

The project includes a local FastMCP server that exposes the second-brain capabilities as tools:

- `search_career_evidence`
- `get_memory_snapshot`
- `build_trajectory_plan`
- `ask_second_brain`

Run it with:

```bash
uv run python capstone/career_mcp_server.py
```

This strengthens the capstone's extensibility story by making the same career intelligence available both through the CLI and through an MCP-compatible tool server.

## Evaluation Plan

The project will compare three versions:

1. Baseline LLM only
2. RAG without memory
3. Full multi-agent system with RAG, memory, and guardrails

Metrics:

- retrieval precision
- groundedness
- personalization quality
- actionability of recommendations
- consistency with stored preferences
- PII leakage rate
- retrieval provenance presence

## How To Build Incrementally

1. Add a small set of real documents under `data/raw/`
2. Implement ingestion and vector search
3. Build retrieval and coach agents
4. Add persistent memory and preference extraction
5. Add PII guardrails
6. Instrument with OTEL
7. Add eval datasets and compare system variants

## Running

To use a local environment file for API keys, create `capstone/.env` from [`capstone/.env.example`](/Users/isabelhong/katas-exercises/katas-exercises/capstone/.env.example) and set:

```bash
ANTHROPIC_API_KEY=your_claude_api_key_here
```

The CLI loads `capstone/.env` automatically at startup.

When the app starts, it prints the active model path so you can confirm whether it is using Claude, Gemini, or the offline fallback.

Current MVP commands:

```bash
uv run python capstone/main.py --query "What role direction should I prioritize next?"
uv run python -m capstone.rag.ingest
uv run python -m capstone.evals.run_evals
```

Running `uv run python -m capstone.evals.run_evals` now writes reproducible artifacts to [`evals/reports/`](/Users/isabelhong/katas-exercises/katas-exercises/capstone/evals/reports).

## Demo Workflow

1. Start with fresh memory:

```bash
uv run python capstone/main.py --reset-memory
```

2. Ask a grounding-heavy question:

```text
What role path fits me best right now?
```

3. Ask a preference question:

```text
I prefer remote backend roles at startups. What should I focus on next?
```

4. Run the evaluation suite:

```bash
uv run python -m capstone.evals.run_evals
```

5. Open the saved report in [`evals/reports/latest_results.md`](/Users/isabelhong/katas-exercises/katas-exercises/capstone/evals/reports/latest_results.md).
