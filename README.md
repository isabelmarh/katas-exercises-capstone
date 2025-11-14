# AI Agent Katas

A collection of practice exercises (katas) for building and evaluating AI agents using [PydanticAI](https://ai.pydantic.dev/) and [pydantic-evals](https://pydantic-evals.pydantic.dev/).

## 🎯 What are AI Agent Katas?

Katas are deliberate practice exercises that help you develop skills through repetition and refinement. These AI agent katas focus on:

- Building autonomous agents that can reason and act
- Evaluating agent performance with structured test cases
- Iterating on agent design based on evaluation results
- Learning different AI agent patterns and architectures

## 🚀 Quick Start

### Install uv

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Get a Gemini API Key

1. Go to [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy your API key
5. Set it as an environment variable:

### Set your Gemini API Key

```bash
# Store your API key in 1Password
# Gemini
op item create --category="API Credential" --title="GEMINI_API_KEY" credential="your-gemini-api-key"
# Claude
op item create --category="API Credential" --title="ANTHROPIC_API_KEY" credential="your-claude-api-key"

# Use it in your shell
# Gemini
export GEMINI_API_KEY=$(op read "op://Private/GEMINI_API_KEY/credential")
# Claude
export ANTHROPIC_API_KEY=$(op read "op://Private/ANTHROPIC_API_KEY/credential")

# Or add to your shell profile (~/.zshrc or ~/.bashrc)
# Gemini
echo 'export GEMINI_API_KEY=$(op read "op://Private/GEMINI_API_KEY/credential")' >> ~/.zshrc
# Claude
echo 'export ANTHROPIC_API_KEY=$(op read "op://Private/ANTHROPIC_API_KEY/credential")' >> ~/.zshrc
```

**N.B.:** If the 1Password desktop app is signed in to multiple accounts is necessary to add the `--account` flag to the commands.
Otherwise, commands may accidentally be executed against the wrong account. The list the signed in accounts run `op account list`
Example:

```bash
# Google Gemini 
echo 'export GEMINI_API_KEY=$(op read "op://Private/GEMINI_API_KEY/credential" --account <ACCOUNT_ID>)' >> ~/.zshrc

# Claude
echo 'export ANTHROPIC_API_KEY=$(op read "op://Private/ANTHROPIC_API_KEY/credential" --account <ACCOUNT_ID>)' >> ~/.zshrc
```

### Running a Kata

```bash
# Sync dependencies
uv sync

# Activate virtual environment
source .venv/bin/activate

# List all available katas
katas list-katas

# Run a specific kata
katas run <kata-name>

# Interactive kata selection
katas run
```

### Checking Setup

Once the setup has been completed you can check your setup by running the `hello-agent` kata. To do this simply execute the following in a virtual environment:

```bash
# If not already done activate virtual environment
source .venv/bin/activate

katas run hello-agent
```

### Creating Your Agent

Here is an example of a simple agent that uses the PydanticAI Agent:

#### Gemini
```python
from pydantic_ai import Agent

agent = Agent(
    model='google-gla:gemini-2.5-pro',
    instructions='Your insructions here',
)
```

#### Claude
```python
from pydantic_ai import Agent

agent = Agent(
    model='anthropic:claude-sonnet-4-5',
    instructions='Your insructions here',
)
```

## 🧪 Evaluation Framework

The evaluation system uses [pydantic-evals](https://pydantic-evals.pydantic.dev/) to:

- Load test cases from `evals.yaml`
- Run your agent against each test case
- Compare outputs against expected results
- Generate detailed performance reports

## 🔍 Observability using Opik

[Opik](https://www.comet.com/docs/opik/) is a tool for monitoring and analyzing your AI agents.

To use Opik, you will need to:

### Clone the Opik repository

```bash
git clone https://github.com/comet-ml/opik.git`
```

### Navigate to the repository

```bash
cd opik
```

### Start the Opik platform

> Note: you will need to have Docker/Colima/Podman installed to run the Opik platform. Also make sure you allocate at least 4 CPUs and 8GB of RAM to the Opik platform.

```bash
./opik.sh
```

###  Python Tracing

Add the following to your agent:

```python
import os
import logfire

os.environ["OTEL_EXPORTER_OTLP_ENDPOINT"] = "http://localhost:5173/api/v1/private/otel"
_ = logfire.configure(send_to_logfire=False, service_name="ai-lsp")
logfire.instrument_pydantic_ai()
logfire.instrument_httpx(capture_all=True)
```

### 󰪮 .NET Tracing

Add the following to your agent:

```csharp
# Agent Framework (2 packages)
dotnet add package Microsoft.Agents.AI --prerelease
dotnet add package Microsoft.Extensions.AI.OpenAI --prerelease

# Hosting (1 package)
dotnet add package Microsoft.Extensions.Hosting

# OpenTelemetry (3 packages)
dotnet add package OpenTelemetry.Exporter.OpenTelemetryProtocol
dotnet add package OpenTelemetry.Extensions.Hosting
dotnet add package OpenTelemetry.Instrumentation.Http
```

And set the following environment variables:

```bash
export OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:5173/api/v1/private/otel/v1/traces
export OTEL_EXPORTER_OTLP_PROTOCOL=http/protobuf
```

## 📖 Learning Resources

- [PydanticAI Documentation](https://ai.pydantic.dev/)
- [Pydantic Evals Documentation](https://ai.pydantic.dev/evals/)
- [Opik](https://www.comet.com/docs/opik/)
- [MCP Documentation](https://modelcontextprotocol.io/docs/getting-started/intro)

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Add your kata or improvements
4. Ensure all evaluations pass
5. Submit a pull request

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

---

**Happy coding! 🎉**
