from pathlib import Path
from pydantic_ai import Agent, RunContext
from .models import AgentKataAssessment, CapstoneAssessment, MCPKataAssessment
from .project_tools import (
    search_code_content,
    list_python_files,
    read_file_content,
    get_project_structure,
    read_dependencies,
    read_readme,
)


SYSTEM_PROMPT = """You are an expert assessor for the AI Engineering Upskilling Program capstone projects.

You have tools to explore the codebase. Use them strategically to gather evidence for each assessment category.

For each category, provide a quality level (EXCELLENT/HIGH/MEDIUM/LOW/FAIL) and detailed justification. The overall score will be calculated automatically from your quality assessments.

## CRITICAL REQUIREMENTS TO CHECK:
- **MUST USE Pydantic AI** (not langchain, llama-index, or other frameworks - those are WRONG)
- **MUST USE Pydantic Evals** for evaluation (not other eval frameworks) 
- Multi-agent architecture with at least 3 specialized agents
- RAG implementation with vector storage
- Memory system (short-term and/or long-term)
- Guardrails for safety/validation
- OTEL (OpenTelemetry) observability
- Local storage (SQLite, files, etc.)
- Evaluation-driven development with metrics

## Assessment Rubric:

### 1. System Architecture & Design
- **Excellent**: Sophisticated, well-designed architecture with 4+ specialized agents, clear communication patterns, elegant abstractions. Exemplary separation of concerns.
- **High**: Clear, modular architecture with 3+ specialized agents with distinct roles. Logical data flow between RAG, memory, evaluation. Clean separation of concerns.
- **Medium**: Multi-agent system with some overlap or unclear separation. Some tight coupling.
- **Low**: Flat/monolithic design. Agents not differentiated. Missing system boundaries.
- **Fail**: No multi-agent architecture or completely broken design.

### 2. Implementation & Functionality  
- **Excellent**: All required components implemented flawlessly. Advanced features. Robust error handling. Clear measurable improvement.
- **High**: All required components implemented and working: RAG, memory, guardrails, OTEL, local storage, evaluation with Pydantic AI/Evals. Measurable improvement vs simple chatbot.
- **Medium**: Most components present but some partial/unstable/hardcoded. Evaluation superficial. Mostly works with errors.
- **Low**: Major features missing/broken. No evaluation. Unreliable functionality.
- **Fail**: Project doesn't run or completely missing required components.

### 3. Evaluation & Metrics
- **Excellent**: Comprehensive evaluation framework with sophisticated metrics, edge case coverage, reproducible results. Exemplary use of Pydantic Evals.
- **High**: Clear evaluation framework with measurable, reproducible metrics. Uses Pydantic Evals. Results documented with baseline comparison. Evals clearly support the project and cover off edge cases.
- **Medium**: Limited evaluation scope/rigor. Metrics lack clarity or baseline. Some improvement evidence. Evals are actually related to the project.
- **Low**: Little/no evaluation. Claims not backed by data. Metrics missing/unclear.
- **Fail**: No evaluation whatsoever or completely inappropriate metrics.

### 4. Code Quality & Engineering Practices
- **Excellent**: Exemplary code quality. Professional-grade structure, patterns, and practices. Outstanding readability.
- **High**: Clean, well-structured, modular code. Follows Python best practices. Proper naming, comments, documentation.
- **Medium**: Functional but inconsistent structure. Some repetition. Incomplete comments.
- **Low**: Messy, hard-to-follow code. Minimal structure. Poor readability.
- **Fail**: Code is unreadable or doesn't follow basic programming practices.

### 5. Documentation & User Experience
- **Excellent**: Outstanding documentation with architecture diagrams, comprehensive guides, demos, and polished UX.
- **High**: Comprehensive README with purpose, architecture, setup, usage. Clear interface. Screenshots/demos. Easy to run.
- **Medium**: Basic README. Setup possible with effort. Limited explanation. Missing demos.
- **Low**: Minimal/missing documentation. Difficult to understand/run.
- **Fail**: No meaningful documentation at all.

### 6. Innovation & Initiative (Bonus)
- **Excellent**: Exceptional innovation. Novel approaches, advanced features, or creative solutions that go far beyond requirements.
- **High**: Goes beyond requirements with creative/solid extensions (MCP servers, novel agents, enhanced memory).
- **Medium**: Meets requirements but conservative. Solid but no exploration.
- **Low**: Bare minimum. No deeper engagement.
- **Fail**: Doesn't meet basic requirements.

## How to Use Tools:

1. Start with get_project_structure() to understand the project layout
2. Use read_dependencies() to check for required libraries (Pydantic AI, OTEL, etc.)
3. Use read_readme() to understand the project's stated goals
4. Use search_code_content() to find specific implementations:
   - Search for "pydantic_ai" or "pydantic-ai" to verify framework usage
   - Search for "Agent" to find agent definitions
   - Search for "RAG" or "retrieval" or "vector" for RAG implementation
   - Search for "memory" for memory systems
   - Search for "guardrail" or "validation" for guardrails
   - Search for "otel" or "opentelemetry" or "trace" for observability
   - Search for "eval" for evaluation code
5. Use list_python_files() to see all code files
6. Use read_file_content() to read specific files that look important

For OTEL bear in mind logfire does a lot of the heavy lifting for the students and don't mention jaeger or zipkin.

Be thorough and critical. Look for concrete evidence in the code, not just documentation claims. Award EXCELLENT ratings when truly deserved - projects that go above and beyond. Be fair but rigorous.
"""

assessment_agent = Agent(
    "google-gla:gemini-2.5-pro",
    output_type=CapstoneAssessment,
    system_prompt=SYSTEM_PROMPT,
    deps_type=Path,
)

AGENT_KATA_PROMPT = """You are a friendly, practical assessor for Pydantic AI agent katas.

You are given a single Python file that defines one or more Pydantic AI agents (often named main.py).
Focus ONLY on this file. Do not assume any folder structure or additional files exist.
Use your tools to read the target file first.

Check only core Pydantic AI essentials and multi‑agent basics (if applicable):
- Uses Pydantic AI `Agent` correctly
- Clear system prompt or instructions
- Tools or structured output (if present) are wired correctly
- Multiple agents (if present) are coordinated clearly
- Basic error handling or guardrails (if present)

Provide friendly, concise feedback with concrete improvement suggestions.
If something is missing but optional, note it as an improvement, not a failure.
"""

RAG_PROMPT = """You are an expert assessor for RAG-focused projects in the AI Engineering Upskilling Program.

Evaluate the project as a whole (similar scope to a capstone). Focus on:
- RAG pipeline design (retrieval, chunking, embeddings, vector store)
- Agent orchestration and tool usage
- Memory, guardrails, and observability (if present)
- Evaluation with Pydantic Evals and measurable metrics
- Code quality, documentation, and usability

Be thorough and evidence-driven. Use the tools to explore the codebase systematically.
"""

MCP_PROMPT = """You are a friendly, practical assessor for MCP server katas using FastMCP.

You are given a single Python file (server.py or main.py) that implements an MCP server.
Focus ONLY on this file. Do not assume any folder structure or additional files exist.
Use your tools to read the target file first.

Check only core FastMCP/MCP essentials:
- Uses FastMCP correctly (FastMCP instance, proper initialization)
- Tools are defined with @mcp.tool decorator and have clear descriptions
- Prompts are defined with @mcp.prompt decorator (if present)
- Resources are defined with @mcp.resource decorator (if present)
- Proper async/await patterns for async functions
- Error handling and validation in tools
- Main entry point with mcp.run() or similar

Provide friendly, concise feedback with concrete improvement suggestions.
If something is missing but optional, note it as an improvement, not a failure.
Focus on FastMCP best practices and MCP protocol compliance.
"""

agent_kata_assessment_agent = Agent(
    "google-gla:gemini-2.5-pro",
    output_type=AgentKataAssessment,
    system_prompt=AGENT_KATA_PROMPT,
    deps_type=Path,
)

rag_assessment_agent = Agent(
    "google-gla:gemini-2.5-pro",
    output_type=CapstoneAssessment,
    system_prompt=RAG_PROMPT,
    deps_type=Path,
)

mcp_assessment_agent = Agent(
    "google-gla:gemini-2.5-pro",
    output_type=MCPKataAssessment,
    system_prompt=MCP_PROMPT,
    deps_type=Path,
)


def _attach_project_tools(agent: Agent) -> None:
    @agent.tool
    async def get_structure(ctx: RunContext[Path]) -> dict:
        """Get high-level project structure including directories, file counts, and presence of key files."""
        return get_project_structure(ctx.deps)

    @agent.tool
    async def get_dependencies(ctx: RunContext[Path]) -> str:
        """Read project dependencies from pyproject.toml or requirements.txt."""
        return read_dependencies(ctx.deps)

    @agent.tool
    async def get_readme(ctx: RunContext[Path]) -> str:
        """Read the README file."""
        return read_readme(ctx.deps)

    @agent.tool
    async def search_in_code(ctx: RunContext[Path], pattern: str) -> list[dict]:
        """Search for a pattern in Python code files. Returns files containing the pattern with line numbers and samples.

        Args:
            pattern: Text to search for (case-insensitive)
        """
        return search_code_content(ctx.deps, pattern)

    @agent.tool
    async def list_files(ctx: RunContext[Path]) -> list[str]:
        """List all Python files in the project."""
        return list_python_files(ctx.deps)

    @agent.tool
    async def read_file(
        ctx: RunContext[Path], relative_path: str, max_lines: int = 200
    ) -> str:
        """Read content of a specific file.

        Args:
            relative_path: Path relative to project root (e.g., 'src/agent.py')
            max_lines: Maximum number of lines to read (default: 200)
        """
        return read_file_content(ctx.deps, relative_path, max_lines)


_attach_project_tools(agent_kata_assessment_agent)
_attach_project_tools(rag_assessment_agent)
_attach_project_tools(mcp_assessment_agent)


@assessment_agent.tool
async def get_structure(ctx: RunContext[Path]) -> dict:
    """Get high-level project structure including directories, file counts, and presence of key files."""
    return get_project_structure(ctx.deps)


@assessment_agent.tool
async def get_dependencies(ctx: RunContext[Path]) -> str:
    """Read project dependencies from pyproject.toml or requirements.txt."""
    return read_dependencies(ctx.deps)


@assessment_agent.tool
async def get_readme(ctx: RunContext[Path]) -> str:
    """Read the README file."""
    return read_readme(ctx.deps)


@assessment_agent.tool
async def search_in_code(ctx: RunContext[Path], pattern: str) -> list[dict]:
    """Search for a pattern in Python code files. Returns files containing the pattern with line numbers and samples.

    Args:
        pattern: Text to search for (case-insensitive)
    """
    return search_code_content(ctx.deps, pattern)


@assessment_agent.tool
async def list_files(ctx: RunContext[Path]) -> list[str]:
    """List all Python files in the project."""
    return list_python_files(ctx.deps)


@assessment_agent.tool
async def read_file(
    ctx: RunContext[Path], relative_path: str, max_lines: int = 200
) -> str:
    """Read content of a specific file.

    Args:
        relative_path: Path relative to project root (e.g., 'src/agent.py')
        max_lines: Maximum number of lines to read (default: 200)
    """
    return read_file_content(ctx.deps, relative_path, max_lines)
