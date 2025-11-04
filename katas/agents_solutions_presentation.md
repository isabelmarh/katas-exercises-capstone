# AI Agent Engineering

Punctuation + Data Contract + Self-Improving

---

# Start Empty

```python
def main(text: str) -> str:
    raise NotImplementedError()
```

---

# Import Agent

```python
from pydantic_ai import Agent

def main(text: str) -> str:
    raise NotImplementedError()
```

---

# Create Agent

```python
from pydantic_ai import Agent

def main(text: str) -> str:
    agent = Agent(model="google-gla:gemini-2.5-pro")
    return agent.run_sync(text).output
```

---

# Add Instructions

```python
instructions = """Add punctuation and capitalization.
Only insert , . ? characters.
Preserve all original words exactly."""

def main(text: str) -> str:
    agent = Agent(
        model="google-gla:gemini-2.5-pro",
        instructions=instructions
    )
    return agent.run_sync(text).output
```

---

# Better Instructions

```python
instructions = """Add proper punctuation and capitalization.

CRITICAL CONSTRAINTS:
- PRESERVE every single word from original
- PRESERVE spelling exactly, even if incorrect
- PRESERVE word order
- ONLY INSERT punctuation: , . ?
- DO NOT add or remove words"""

def main(text: str) -> str:
    agent = Agent(
        model="google-gla:gemini-2.5-pro",
        instructions=instructions
    )
    return agent.run_sync(text).output
```

---

# Test It

```bash
uv run python -m katas.punctuation.main
```

Input: `"hello world how are you today"`
Output: `"Hello, world. How are you today?"`

---

# Evaluation: Already Built

```python
# We have test cases defined in the kata
punctuation_dataset = Dataset[str, str, Any](
    cases=[
        Case(name="simple_sentence", ...),
        Case(name="acronym_caps", ...),
        Case(name="clause_commas", ...),
        # ... 7 total test cases
    ]
)
```

---

# Run Tests

```bash
uv run python -m katas.punctuation.main
```

```
✅ simple_sentence: PASSED
✅ clause_commas: PASSED
❌ acronym_caps: FAILED
   Expected: "CIA operative said go now."
   Got: "Cia operative said go now."
✅ multiple_questions: PASSED
```

---

# Observability: Logfire

```python
import logfire

logfire.configure()
```

---

# Instrument Agent

```python
def main(text: str) -> str:
    agent = Agent(
        model="google-gla:gemini-2.5-pro",
        instructions=instructions
    )
    
    with logfire.span("punctuation_agent"):
        return agent.run_sync(text).output
```

---

# View Traces

```bash
# Run your agent
uv run python -m katas.punctuation.main

# Open Logfire dashboard
# See: Agent calls, token usage, latency, prompts
```

---

# Data Contract: Structured Output

```python
from open_data_contract import OpenDataContractStandardOdcs

def main(unstructured_input: str) -> str:
    agent = Agent(
        model="google-gla:gemini-2.5-pro",
        output_type=OpenDataContractStandardOdcs
    )
    response = agent.run_sync(unstructured_input).output
    return str(response)
```

---

# Generate Pydantic Models

```bash
datamodel-codegen \
  --url https://raw.githubusercontent.com/datacontract/\
datacontract-specification/main/datacontract.schema.json \
  --output open_data_contract.py
```

---

# Input Example

```python
input_text = """Customer orders with:
- Order ID (UUID)
- Customer email (PII)
- Order timestamp
- Total amount in cents
- Status (pending, completed, cancelled)

Updated daily, 24h latency, 2 year retention."""
```

---

# Output: Valid YAML

```yaml
dataContractSpecification: 1.1.0
id: customer-orders
info:
  title: Customer Orders
  version: 1.0.0
models:
  orders:
    fields:
      order_id:
        type: text
        format: uuid
        primaryKey: true
```

---

# Custom Validation

```python
from pydantic import field_validator

class DataContract(BaseModel):
    email: str
    
    @field_validator('email')
    @classmethod
    def validate_email(cls, v: str) -> str:
        if '@' not in v:
            raise ValueError('Invalid email')
        return v
```

---

# Tools: Web Search

```python
from pydantic_ai import Agent
from pydantic_ai.tools import web_search

agent = Agent(
    model="openai:gpt-4",
    tools=[web_search]
)

# Agent can now search the web when needed
result = agent.run_sync(
    "What's the current price of Bitcoin?"
)
```

---

# Tool Gotcha: Gemini API

❌ Gemini doesn't support tools + structured output:
```python
agent = Agent(
    model="google-gla:gemini-2.5-pro",
    tools=[web_search],
    output_type=MyModel  # ERROR with Gemini!
)
```

✅ Use a different model (OpenAI, Claude):
```python
agent = Agent(
    model="openai:gpt-4",
    tools=[web_search],
    output_type=MyModel  # Works!
)
```

---

# Self-Improving Agent Demo

```bash
# Watch agent improve itself over multiple runs
uv run python -m katas.self-improving-agent.main

# Run 1: ❌ 3 failures
# Run 2: ❌ 1 failure  
# Run 3: ✅ All passed

# Agent loads instructions from file
# Collects failures from evaluation
# Uses improver agent to fix instructions
# Saves improved instructions back to file
# Next run uses better instructions!
```

---

# Key Patterns

```python
# Basic agent
agent = Agent(model="...", instructions="...")
agent.run_sync(input).output

# Structured output
agent = Agent(model="...", output_type=MyModel)

# With tools
agent = Agent(model="...", tools=[web_search])

# Evaluation
report = dataset.evaluate_sync(main)
```

---

# Common Mistakes

❌ Vague instructions
❌ No evaluation
❌ Using Gemini with tools + structured output
❌ Not using structured outputs when needed
❌ Ignoring validation

---

# Tools

```bash
# Run
uv run python -m katas.punctuation.main

# Observe
logfire dashboard

# Evaluate
report.print()
```

---

# Next: Try Other Katas

- Code Review Bot
- Commit Message Generator
- Data Glossary Audit

---

# Resources

- `pydantic.ai` - Agent framework
- `pydantic-evals` - Evaluation
- `logfire.dev` - Observability
- `/katas` - Practice exercises

---

# Demo Time 🚀

Let's build and improve an agent live!