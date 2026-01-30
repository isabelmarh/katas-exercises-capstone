# Capstone Assessor

AI-powered agentic assessment tool for AI Engineering Upskilling Program capstone projects using Pydantic AI.

## Features

- **Agentic Code Exploration**: Uses AI agent with tools to dynamically explore codebases
- **Smart Assessment**: Agent searches for evidence in actual code, not just documentation
- **No Assumptions**: Doesn't assume project structure - discovers it through exploration
- **Comprehensive Evaluation**: Covers 6 key areas with detailed scoring and feedback
- **Beautiful Reports**: Generates slick HTML reports with scores, ratings, and actionable feedback

## How It Works

The assessment agent uses tools to explore your project:

1. **get_structure** - Analyzes directory layout and file organization
2. **get_dependencies** - Checks for required libraries (Pydantic AI, OTEL, etc.)
3. **get_readme** - Reads project documentation
4. **search_in_code** - Finds specific implementations:
   - Searches for "pydantic_ai" or "Agent" to verify framework usage ✅
   - Finds "RAG", "retrieval", "vector" for RAG implementation
   - Locates "memory" for memory systems
   - Checks for "guardrail" or "validation"
   - Confirms "otel" or "opentelemetry" or "trace" for observability
   - Validates "eval" for evaluation framework
5. **list_files** - Lists all Python files
6. **read_file** - Reads specific files for detailed analysis

### ⚠️ Critical Requirements

The agent specifically checks for:

- ✅ **Pydantic AI** (REQUIRED) - langchain, llama-index, etc. are WRONG
- ✅ **Pydantic Evals** (REQUIRED) - for evaluation framework
- ✅ Multi-agent architecture (3+ agents)
- ✅ RAG implementation with vector storage
- ✅ Memory system (short/long-term)
- ✅ Guardrails for safety
- ✅ OTEL observability
- ✅ Local storage
- ✅ Evaluation with metrics

## Assessment Categories

1. **System Architecture & Design** - Multi-agent architecture, modularity, data flow
2. **Implementation & Functionality** - RAG, memory, guardrails, OTEL, evaluation
3. **Evaluation & Metrics** - Measurement framework, baseline comparison, reproducibility
4. **Code Quality & Engineering** - Structure, best practices, documentation
5. **Documentation & User Experience** - README, setup instructions, demos
6. **Innovation & Initiative** - Creative extensions beyond requirements

## Installation

```bash
uv sync
```

## Usage

### Assess a project directory

```bash
uv run capstone-assessor assess /path/to/project
```

The agent will explore the codebase and generate a comprehensive assessment.

### Assess with custom output

```bash
uv run capstone-assessor assess /path/to/project --output report.html --name "My Awesome Project"
```

### Test with example project

```bash
uv run capstone-assessor assess example_project --name "Multi-Agent RAG System"
```

### View assessment info

```bash
uv run capstone-assessor info
```

## Environment Setup

Set your Anthropic API key:

```bash
export ANTHROPIC_API_KEY=your_api_key_here
```

## Output

The tool generates a beautiful HTML assessment report with:

- Overall rating (High/Medium/Low Quality)
- Numeric score out of 100
- Detailed assessment for each category with evidence from code
- Quality badges with scores
- Key strengths identified
- Areas for improvement
- Summary feedback

## Example

```bash
uv run capstone-assessor assess ./my-capstone-project
```

The agent will:
1. Explore project structure
2. Check dependencies for Pydantic AI
3. Search for multi-agent architecture
4. Verify RAG implementation
5. Check for memory, guardrails, OTEL
6. Review evaluation framework
7. Assess code quality
8. Generate comprehensive HTML report

## Development

Built with:
- [Pydantic AI](https://ai.pydantic.dev/) - AI agent framework with tools
- [Typer](https://typer.tiangolo.com/) - CLI framework
- [Rich](https://rich.readthedocs.io/) - Terminal formatting
- [Pydantic](https://docs.pydantic.dev/) - Data validation
- Claude Sonnet 4 - LLM for assessment

## Author

[@benomahony](https://github.com/benomahony)
