# AI Agent Katas

A collection of practice exercises (katas) for building and evaluating AI agents
using [PydanticAI](https://ai.pydantic.dev/) and [pydantic-evals](https://pydantic-evals.pydantic.dev/).

## What are AI Agent Katas?

Katas are deliberate practice exercises that help you develop skills through repetition and refinement. These AI agent
katas focus on:

- Building autonomous agents that can reason and act
- Evaluating agent performance with structured test cases
- Iterating on agent design based on evaluation results
- Learning different AI agent patterns and architectures

## Quick Start

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

**N.B.:** If the 1Password desktop app is signed in to multiple accounts is necessary to add the `--account` flag to the
commands.
Otherwise, commands may accidentally be executed against the wrong account. The list the signed in accounts run
`op account list`
Example:

```bash
# Google Gemini 
echo 'export GEMINI_API_KEY=$(op read "op://Private/GEMINI_API_KEY/credential" --account <ACCOUNT_ID>)' >> ~/.zshrc

# Claude
echo 'export ANTHROPIC_API_KEY=$(op read "op://Private/ANTHROPIC_API_KEY/credential" --account <ACCOUNT_ID>)' >> ~/.zshrc
```

## Setup

### Project Structure Requirements

- The `rag` or `capstone` directory **must exist** in the specified path  
- Create these folders at the **root directory**  
- Place your capstone/rag project folder **inside the corresponding directory**

```
root/
├── rag/
│   └── your-project/
├── capstone/
│   └── your-project/
```

### Branch Setup

Run the interactive setup to create and configure a Git branch.  
**Note:** Keep your branch name the same as your GitHub ID.

```bash
katas start
```


### Running a Kata

```bash
# Sync dependencies
uv sync

# Sync all dependencies for all katas (agents, MCP, RAG)
uv sync --all-packages --all-groups --all-extras

# Activate virtual environment
source .venv/bin/activate

# List all available katas
katas list

# Run a specific kata
katas run <kata-name>

# Interactive kata selection
katas run

# Interactive CLI interaction with CLI chat 
katas chat


katas web
```

### Checking Setup

Once the setup has been completed you can check your setup by running the `hello-agent` kata. To do this simply execute
the following in a virtual environment:

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

## Assessment

### Interactive assessment (choose Agent / MCP / RAG / Capstone)

```bash
katas assess
```
### Assess Agent or MCP katas by path
- Lists available agents
```bash
katas assess katas
```      
- Lists available MCP servers
```bash
katas assess mcp_katas
``` 

**Note:** Reports will be saved to respective folders under assessment_report   

### Assess a specific RAG or Capstone project by path
- rag - ```katas assess /path/to/rag/<your-folder>```

- capstone - ```katas assess /path/to/capstone/<your-folder>```


### Bulk Assess Command

### Command
```bash
katas bulk-assess
```

### Description
Runs bulk assessment on multiple Git branches using default configuration settings.

### Git Repository
- Repository Path: Defaults to the current working directory
- Run the command from the root of the Git repository

### Branch Input Options
You can provide branch names using one of the following methods:

1. Provide Branches Directly
- Pass branch names as a comma-separated list
- Example:
  feature/login,bugfix/api-timeout,release/v1.2

2. Read Branches from File
- Provide a file (e.g., branches.txt)
- Each branch name must be on a new line
- Example (branches.txt):
  feature/login
  bugfix/api-timeout
  release/v1.2

### Assessment Settings
- Other Options: Default values are used

### Output
- A separate report is generated for each branch
- Reports are saved under:
```exports/<branch-name>/```

### Notes
- Ensure the branches exist in the repository before running the command
- Existing reports with the same branch name may be overwritten


## Evaluation Framework

The evaluation system uses [pydantic-evals](https://pydantic-evals.pydantic.dev/) to:

- Load test cases from `evals.yaml`
- Run your agent against each test case
- Compare outputs against expected results
- Generate detailed performance reports

## Observability with Arize Phoenix

[Arize Phoenix](https://arize.com/docs/phoenix/) is an open-source LLM observability platform. Use it to trace requests made by your agents to LLMs and tools.

### Quick Start

1. Run Phoenix locally:

   ```bash
   uvx arize-phoenix serve
   ```

2. Open <http://127.0.0.1:6006> to see the Phoenix UI.

3. Follow the [Phoenix setup guide](arize_phoenix_setup.md) to add tracing to your agents.

## Learning Resources

- [PydanticAI Documentation](https://ai.pydantic.dev/)
- [Pydantic Evals Documentation](https://ai.pydantic.dev/evals/)
- [Arize Phoenix](https://arize.com/docs/phoenix/)
- [MCP Documentation](https://modelcontextprotocol.io/docs/getting-started/intro)

## Contributing

Contributions are welcome! If you have ideas for Katas or improvements to the CLI please reach out to the maintainers!

>[!WARNING]
>Assignment solutions are not contributions! Do not push these to main, we will make fun of you for it.

## License

This project is open source and available under the [MIT License](LICENSE).
