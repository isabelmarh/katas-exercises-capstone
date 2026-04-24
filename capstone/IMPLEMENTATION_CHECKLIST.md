# Career Compass Implementation Checklist

## Phase 1: Project Setup

- [ ] Update [`pyproject.toml`](/Users/isabelhong/katas-exercises/katas-exercises/capstone/pyproject.toml) with the dependencies you choose for:
  - `pydantic-ai`
  - `pydantic-evals`
  - `opentelemetry-api`
  - `opentelemetry-sdk`
  - local vector store client such as `qdrant-client` or `chromadb`
  - embedding model dependencies
- [ ] Implement the CLI loop in [`main.py`](/Users/isabelhong/katas-exercises/katas-exercises/capstone/main.py)
- [ ] Wire the orchestration entry point in [`app.py`](/Users/isabelhong/katas-exercises/katas-exercises/capstone/app.py)

## Phase 2: Local Data and RAG

- [ ] Add real documents under [`data/raw/`](/Users/isabelhong/katas-exercises/katas-exercises/capstone/data/raw)
- [ ] Implement document chunking in [`rag/chunking.py`](/Users/isabelhong/katas-exercises/katas-exercises/capstone/rag/chunking.py)
- [ ] Implement embedding generation in [`rag/embeddings.py`](/Users/isabelhong/katas-exercises/katas-exercises/capstone/rag/embeddings.py)
- [ ] Implement local vector storage in [`rag/vector_store.py`](/Users/isabelhong/katas-exercises/katas-exercises/capstone/rag/vector_store.py)
- [ ] Implement ingestion flow in [`rag/ingest.py`](/Users/isabelhong/katas-exercises/katas-exercises/capstone/rag/ingest.py)

## Phase 3: Agents

- [ ] Implement query classification in [`agents/router_agent.py`](/Users/isabelhong/katas-exercises/katas-exercises/capstone/agents/router_agent.py)
- [ ] Implement semantic retrieval in [`agents/retrieval_agent.py`](/Users/isabelhong/katas-exercises/katas-exercises/capstone/agents/retrieval_agent.py)
- [ ] Implement grounded recommendations in [`agents/career_coach_agent.py`](/Users/isabelhong/katas-exercises/katas-exercises/capstone/agents/career_coach_agent.py)
- [ ] Implement memory read/write helpers in [`agents/memory_agent.py`](/Users/isabelhong/katas-exercises/katas-exercises/capstone/agents/memory_agent.py)

## Phase 4: Memory and Guardrails

- [ ] Implement SQLite schema and persistence in [`memory/store.py`](/Users/isabelhong/katas-exercises/katas-exercises/capstone/memory/store.py)
- [ ] Implement conversation summarization or preference extraction in [`memory/summarizer.py`](/Users/isabelhong/katas-exercises/katas-exercises/capstone/memory/summarizer.py)
- [ ] Implement PII redaction in [`guardrails.py`](/Users/isabelhong/katas-exercises/katas-exercises/capstone/guardrails.py)
- [ ] Apply redaction before writing memory and optionally before returning responses

## Phase 5: Observability

- [ ] Configure tracing in [`telemetry.py`](/Users/isabelhong/katas-exercises/katas-exercises/capstone/telemetry.py)
- [ ] Add spans around routing, retrieval, synthesis, ingestion, and memory writes
- [ ] Record useful attributes such as route choice, top-k count, latency, and memory usage

## Phase 6: Evaluation-Driven Development

- [ ] Define test cases in [`evals/datasets.py`](/Users/isabelhong/katas-exercises/katas-exercises/capstone/evals/datasets.py)
- [ ] Implement evaluators in [`evals/evaluators.py`](/Users/isabelhong/katas-exercises/katas-exercises/capstone/evals/evaluators.py)
- [ ] Compare baseline, RAG-only, and full system in [`evals/run_evals.py`](/Users/isabelhong/katas-exercises/katas-exercises/capstone/evals/run_evals.py)
- [ ] Save results as a markdown or JSON report under `assessment_report` if desired

## Recommended MVP Milestones

- [ ] Milestone 1: CLI + ingestion + retrieval works on 5 to 10 documents
- [ ] Milestone 2: recommendations are grounded in retrieved evidence
- [ ] Milestone 3: memory persists preferences across sessions
- [ ] Milestone 4: evals show measurable improvement over baseline
- [ ] Milestone 5: OTEL traces and README are demo-ready

## Good Starter Questions For Your Eval Dataset

- [ ] What role path fits me best right now based on my projects?
- [ ] What evidence supports backend engineering as a better fit than frontend?
- [ ] What skill gaps appear most often in the job descriptions I saved?
- [ ] What should I study over the next 30 days if I want to move toward AI engineering?
- [ ] What preferences have I stated about remote work, leadership, or company size?
- [ ] If I include an email or phone number in chat, does memory redact it before persistence?
