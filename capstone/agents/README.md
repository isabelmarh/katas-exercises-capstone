# Career Compass Agents

This folder contains the Pydantic AI agents used by the Career Compass capstone:

- `router_agent.py`: classifies whether a query needs retrieval, memory, or direct handling
- `preference_agent.py`: extracts stable user preferences such as remote/hybrid, role interest, and company style
- `baseline_agent.py`: simple non-RAG comparison agent for evals
- `career_coach_agent.py`: synthesizes retrieved evidence and memory into a grounded recommendation
- `trajectory_agent.py`: structured career-path and skill-gap planner using Pydantic AI tools and output validation
- `retrieval_agent.py`: bridges the agents to the local RAG index in `../rag/`
- `memory_agent.py`: bridges the agents to the SQLite memory store in `../memory/`

## Orchestration

Agent coordination happens in [`../app.py`](/Users/isabelhong/katas-exercises/katas-exercises/capstone/app.py), not inside one monolithic agent file.

The orchestration flow is:

1. sanitize the incoming query with guardrails
2. route the query
3. extract preferences
4. retrieve relevant career evidence
5. optionally invoke the trajectory planner, which uses agent tools to fetch evidence and memory
6. sanitize the answer
7. persist the conversation, preferences, and episodic memory

This separation is intentional so the capstone shows explicit collaboration between agents, RAG, memory, and guardrails.
