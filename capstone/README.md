# Career Compass Second Brain

Career Compass Second Brain is a local multi-agent system that helps me decide my next software career step using my own documents, reflections, saved job descriptions, and conversation history.

The project is designed to satisfy the "Second Brain" capstone requirements by combining:

- Pydantic AI for agent orchestration
- Pydantic Evals for evaluation-driven development
- OpenTelemetry for observability
- RAG for semantic retrieval over local career documents
- Persistent memory for conversation history and preferences
- Guardrails to redact PII before saving memory

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
- [`agents/`](/Users/isabelhong/katas-exercises/katas-exercises/capstone/agents): specialized agents
- [`rag/`](/Users/isabelhong/katas-exercises/katas-exercises/capstone/rag): chunking, embeddings, vector search, ingestion
- [`memory/`](/Users/isabelhong/katas-exercises/katas-exercises/capstone/memory): SQLite memory store and summarization helpers
- [`guardrails.py`](/Users/isabelhong/katas-exercises/katas-exercises/capstone/guardrails.py): PII redaction before persistence
- [`telemetry.py`](/Users/isabelhong/katas-exercises/katas-exercises/capstone/telemetry.py): OTEL setup
- [`evals/`](/Users/isabelhong/katas-exercises/katas-exercises/capstone/evals): datasets and evaluators
- [`IMPLEMENTATION_CHECKLIST.md`](/Users/isabelhong/katas-exercises/katas-exercises/capstone/IMPLEMENTATION_CHECKLIST.md): step-by-step build plan

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

## How To Build Incrementally

1. Add a small set of real documents under `data/raw/`
2. Implement ingestion and vector search
3. Build retrieval and coach agents
4. Add persistent memory and preference extraction
5. Add PII guardrails
6. Instrument with OTEL
7. Add eval datasets and compare system variants

## Running

This scaffold is intentionally minimal. As implementation progresses, the intended commands are:

```bash
uv run python capstone/main.py --query "What role direction should I prioritize next?"
uv run python -m capstone.rag.ingest
uv run python -m capstone.evals.run_evals
```
