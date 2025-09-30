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
op item create --category="API Credential" --title="GEMINI_API_KEY" credential="your-gemini-api-key"

# Use it in your shell
export GEMINI_API_KEY=$(op read "op://Private/GEMINI_API_KEY/credential")

# Or add to your shell profile (~/.zshrc or ~/.bashrc)
echo 'export GEMINI_API_KEY=$(op read "op://Private/GEMINI_API_KEY/credential")' >> ~/.zshrc
```

**N.B.:** If the 1Password desktop app is signed in to multiple accounts is necessary to add the `--account` flag to the commands. 
Otherwise, commands may accidentally be executed against the wrong account. The list the signed in accounts run `op account list`
Example:

```bash
echo 'export GEMINI_API_KEY=$(op read "op://Private/GEMINI_API_KEY/credential" --account <ACCOUNT_ID>)' >> ~/.zshrc
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

## 🏗️ Kata Structure

Each kata follows a consistent structure:

```bash
katas/<kata-name>/
├── README.md         # Kata description and goals
├── evals.yaml        # Test cases and evaluation criteria
├── main.py           # Your agent implementation
└── pyproject.toml    # Kata-specific dependencies
```

### Creating Your Agent

Here is an example of a simple agent that uses the PydanticAI Agent:

```python
from pydantic_ai import Agent

agent = Agent(
    model='google-gla:gemini-2.5-pro',
    instructions='Your insructions here',
)
```

## 🧪 Evaluation Framework

The evaluation system uses [pydantic-evals](https://pydantic-evals.pydantic.dev/) to:

- Load test cases from `evals.yaml`
- Run your agent against each test case
- Compare outputs against expected results
- Generate detailed performance reports

## 📖 Learning Resources

- [PydanticAI Documentation](https://ai.pydantic.dev/)
- [Pydantic Evals Documentation](https://ai.pydantic.dev/evals/)

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
