# AI Agent Katas

### Practice Building & Evaluating AI Agents

Ben O'Mahony
@benomahony

---

# What Are AI Agents?

Autonomous systems that can:

- **Reason** about complex problems
- **Act** using tools and APIs  
- **Learn** from feedback
- **Adapt** to new situations

Unlike simple chatbots, agents have goals and take actions to achieve them.

---

# The Kata Approach

**Kata** (型): A deliberate practice exercise focused on mastery through repetition

For AI Agents:

- Small, focused exercises
- Clear success criteria
- Immediate feedback
- Iterative improvement

Learn by doing, not just reading.

---

# Why Evals-Driven Development?

Traditional AI development:

```python
prompt = "Do the thing"
response = llm(prompt)
print(response)  # 🤞 Hope it works
```

Evals-driven development:

```python
dataset = Dataset(cases=[...])
agent = build_agent()
report = dataset.evaluate_sync(agent)
# ✅ Know it works
```

---

# Evals-Driven Development

**Test-Driven Development for AI**

1. Define test cases with expected outputs
2. Build your agent
3. Run evaluations
4. Iterate based on results
5. Achieve measurable improvement

Move from "vibes-based" to data-driven AI development.

---

# Enter PydanticAI

Type-safe AI agent framework:

```python
from pydantic_ai import Agent

agent = Agent(
    model='google-gla:gemini-2.5-pro',
    instructions='Your clear instructions here'
)

result = agent.run_sync("user input")
```

Built on Pydantic's validation and type safety.

---

# Pydantic-Evals

Structured evaluation framework:

```python
from pydantic_evals import Case, Dataset
from pydantic_evals.evaluators import EqualsExpected

dataset = Dataset(
    cases=[
        Case(
            name="test_greeting",
            inputs="Say hello",
            expected_output="Hello!",
            evaluators=(EqualsExpected(),)
        )
    ]
)
```

---

# Evaluator Types

**EqualsExpected**: Exact string match

```python
EqualsExpected()
```

**Contains**: Check for substring

```python
Contains(substring="key phrase")
```

**LLMJudge**: AI-powered evaluation

```python
LLMJudge(criteria="Response is helpful and accurate")
```

Mix and match based on your needs.

---

# Kata Structure

```
katas/<kata-name>/
├── README.md         # Challenge description
├── main.py           # Your implementation
└── pyproject.toml    # Dependencies
```

Each kata:

- Has inline test cases
- Provides clear constraints
- Offers immediate feedback

---

# Example: Punctuation Kata

**Goal**: Add punctuation and capitalization without changing words

Input:

```
hello world how are you today
```

Expected Output:

```
Hello, world. How are you today?
```

7 test cases from easy to hard complexity.

---

# Running a Kata

```bash
# List available katas
katas list-katas

# Run specific kata
katas run punctuation

# Interactive selection
katas run
```

Instant feedback loop:

- See which tests pass/fail
- Understand why
- Iterate quickly

---

# The Feedback Loop

```
1. Write Evals      (Red)
         ↓
2. Build Agent      (Green)
         ↓
3. Run & Analyze
         ↓
4. Improve Agent    (Refactor)
         ↓
    (Repeat)
```

Just like TDD, but for AI agents.

---

# Available Katas

- **hello-agent**: Setup verification
- **punctuation**: Text formatting rules
- **commit-message-generator**: Conventional commits
- **data-glossary-audit**: Data quality checks
- **code-review-bot**: PR review automation
- **datacontract**: Contract validation
- **self-improving-agent**: Meta-learning

From basic to advanced patterns.

---

# Getting Started

```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone repo
git clone https://github.com/twlabs/katas-exercises/
cd ai-agent-katas

# Setup environment
uv sync
source .venv/bin/activate

# Set API key
export GEMINI_API_KEY="your-key"

# Verify setup
katas run hello-agent
```

---

# Key Takeaways

✅ AI agents are autonomous systems that reason and act

✅ Evals-driven development provides measurable improvement

✅ PydanticAI + pydantic-evals = type-safe agents with structured testing

✅ Katas offer hands-on practice with immediate feedback

✅ Start small, iterate fast, build confidence

---

# Resources

**Repository**: <https://github.com/benomahony/ai-agent-katas>

**PydanticAI Docs**: <https://ai.pydantic.dev/>

**Pydantic-Evals Docs**: <https://pydantic-evals.pydantic.dev/>

**Questions?**

---

# Let's Build Some Agents! 🚀

```bash
katas run
```
