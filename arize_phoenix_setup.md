# Adding Arize Phoenix to a PydanticAI Project

## Introduction

This guide walks you through setting up **Arize Phoenix**, an open-source AI observability platform, to monitor and debug your PydanticAI agents. By the end, you'll have traces flowing from your agents into Phoenix for visualization and debugging.

We present two quick-start approaches (choose based on your needs) and a manual setup section for those who want to understand the underlying machinery.

---

## Background: What's Actually Happening?

Before diving in, here's the 30-second version of what we're setting up:

1. **PydanticAI** emits **traces** (detailed records of agent execution)
2. Traces are sent using **OpenTelemetry** (an industry-standard observability protocol)
3. **Phoenix** receives and visualizes these traces

The approaches below configure this same pipeline—they differ in what *semantic conventions* they use (which affects how rich the Phoenix visualizations are).

### Key Concepts

| Component | What It Does |
|-----------|--------------|
| **TracerProvider** | Central configuration object that manages trace creation |
| **SpanProcessor** | Processes spans before export (can transform, filter, or batch) |
| **SpanExporter** | Sends spans to a backend (Phoenix) via OTLP protocol |
| **Span** | A unit of work—an LLM call, a tool invocation, an agent run |
| **Trace** | A tree of related spans representing a complete operation |

### Semantic Conventions: OTel GenAI vs OpenInference

There are two ways to format AI/LLM trace data:

| Convention | Used By | Phoenix Support |
|------------|---------|-----------------|
| **OTel GenAI** | Industry standard, PydanticAI native | Good — traces display correctly |
| **OpenInference** | Arize ecosystem (Phoenix, Arize AX) | Best — richer visualizations, conversation threading, session attribution |

Both work with Phoenix. OpenInference unlocks additional features but ties you to the Arize ecosystem. OTel GenAI is portable to any OpenTelemetry-compatible backend (Jaeger, Datadog, Honeycomb, etc.).

---

## Which Approach Should I Use?

| Approach | When to Use |
|----------|-------------|
| **Quick Start: OpenInference** | You want the richest Phoenix experience and don't need portability to other backends |
| **Quick Start: Standard OTel** | You want portability, or prefer fewer dependencies |
| **Manual Setup** | You want to understand the internals, or need custom configuration |

**Our recommendation**: Start with **Quick Start: OpenInference** for the best Phoenix experience. If you later need portability, switching to Standard OTel is straightforward.

---

## Running Phoenix

Regardless of which approach you choose, you need Phoenix running to receive traces.

**Quickest option** (using uvx):
```bash
uvx arize-phoenix serve
```

**Alternative** (using pip):
```bash
pip install arize-phoenix
python -m phoenix.server.main serve
```

**Alternative** (using Docker):
```bash
docker run -d -p 6006:6006 arizephoenix/phoenix:latest
```

Phoenix will be available at **http://127.0.0.1:6006**. Open this in your browser to see the UI.

---

## Quick Start: OpenInference

This approach gives you the richest Phoenix experience with automatic instrumentation.

### Install Dependencies

```bash
pip install pydantic-ai arize-phoenix-otel openinference-instrumentation-pydantic-ai
```

### Configure Tracing

```python
from phoenix.otel import register
from pydantic_ai import Agent

register(project_name="my-app", auto_instrument=True)
Agent.instrument_all()
```

Here's what's happening:

- **`register()`** sets up a TracerProvider, SpanProcessor, and Exporter with sensible defaults
- **`project_name`** labels your traces in Phoenix for easy filtering
- **`auto_instrument=True`** registers the OpenInference span processor to enrich traces with Arize-specific attributes
- **`Agent.instrument_all()`** enables PydanticAI to emit traces (required — see note below)

> **Note:** Unlike other OpenInference packages (OpenAI, LangChain) which auto-patch their libraries, the PydanticAI package is a *span processor* that enriches existing spans. You must explicitly enable PydanticAI's instrumentation via `Agent.instrument_all()` or by passing `instrument=True` to individual agents.

By default, traces are sent to `http://127.0.0.1:6006`.

### Complete Example

```python
import asyncio
from phoenix.otel import register
from pydantic_ai import Agent

# Configure tracing (must be called before creating agents)
register(project_name="weather-app", auto_instrument=True)
Agent.instrument_all()

# Create your agent
agent = Agent(
    "anthropic:claude-sonnet-4-5",
    instructions="You are a helpful weather assistant.",
)

@agent.tool
def get_weather(city: str) -> str:
    """Get the current weather for a city."""
    return f"The weather in {city} is sunny and 22°C"

async def main():
    result = await agent.run("What's the weather in Melbourne?")
    print(result.output)

if __name__ == "__main__":
    asyncio.run(main())
```

Run this, then open http://127.0.0.1:6006 to see your trace.

### Configuration Options

```python
register(
    project_name="my-app",
    endpoint="http://127.0.0.1:6006/v1/traces",  # Custom endpoint
    auto_instrument=True,
    batch=True,  # Batch spans for better performance (slight delay)
)
```

You can also configure the endpoint via environment variable:
```bash
export OTEL_EXPORTER_OTLP_ENDPOINT=http://127.0.0.1:6006
```

---

## Quick Start: Standard OTel

This approach uses industry-standard OpenTelemetry semantic conventions (OTel GenAI). Traces work with Phoenix and any other OTel-compatible backend (Jaeger, Datadog, Honeycomb, etc.) — no Arize-specific dependencies.

### Install Dependencies

```bash
pip install pydantic-ai arize-phoenix-otel
```

### Configure Tracing

```python
from phoenix.otel import register
from pydantic_ai import Agent

register(project_name="my-app")
Agent.instrument_all()
```

Key differences from the OpenInference approach:
- No `auto_instrument=True` (we're not using OpenInference)
- Explicit `Agent.instrument_all()` enables PydanticAI's native instrumentation

The rest of your code (agent creation, tools, etc.) remains identical to the OpenInference example above.

---

## Manual Setup

This section shows how to configure OpenTelemetry explicitly. Use this if you want to:
- Understand what the quick-start helpers abstract away
- Customize the configuration (custom Resource, multiple processors, etc.)
- Learn transferable OTel skills that work with any backend

### Base Configuration (Standard OTel)

Create a `tracing.py` module:

```python
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor, BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource

_initialized = False

def init_tracing(
    endpoint: str = "http://127.0.0.1:6006/v1/traces",
    service_name: str = "pydantic-ai-app",
    batch: bool = False,
) -> None:
    """Initialize OpenTelemetry tracing to send spans to Phoenix."""
    global _initialized
    if _initialized:
        return

    # Resource identifies this service in traces
    resource = Resource.create({"service.name": service_name})

    # TracerProvider is the central configuration object
    tracer_provider = TracerProvider(resource=resource)

    # Exporter sends spans to Phoenix via OTLP
    exporter = OTLPSpanExporter(endpoint=endpoint)

    # Choose processor based on use case (see note below)
    if batch:
        tracer_provider.add_span_processor(BatchSpanProcessor(exporter))
    else:
        tracer_provider.add_span_processor(SimpleSpanProcessor(exporter))

    # Register as the global tracer provider
    trace.set_tracer_provider(tracer_provider)

    _initialized = True
```

**SimpleSpanProcessor vs BatchSpanProcessor:**

| Processor | Behavior | Use When |
|-----------|----------|----------|
| `SimpleSpanProcessor` | Exports each span immediately | Learning, debugging, development — traces appear instantly in Phoenix |
| `BatchSpanProcessor` | Buffers spans and exports in batches | Production — more efficient, but slight delay before traces appear |

For this guide, we default to `SimpleSpanProcessor` so you get immediate feedback. In production, pass `batch=True` for better performance.

Use it in your application by replacing the tracing setup from the Quick Start examples:

```python
from tracing import init_tracing

# Initialize tracing BEFORE creating agents
init_tracing(service_name="weather-app")

# Enable PydanticAI's native instrumentation
Agent.instrument_all()

# ... rest of your agent code (same as Quick Start examples)
```

**Dependencies:**
```bash
pip install pydantic-ai opentelemetry-api opentelemetry-sdk opentelemetry-exporter-otlp
```

**Graceful shutdown (production):**

When using `BatchSpanProcessor`, spans are buffered in memory. If your application exits abruptly, buffered spans may be lost. To ensure all traces are exported before shutdown:

```python
from opentelemetry import trace

# At application shutdown (e.g., in a finally block or signal handler)
tracer_provider = trace.get_tracer_provider()
if hasattr(tracer_provider, 'shutdown'):
    tracer_provider.shutdown()  # Flushes pending spans and releases resources
```

This isn't needed with `SimpleSpanProcessor` since spans are exported immediately.

### Adding OpenInference (Optional)

To get richer Phoenix visualizations, add the OpenInference span processor. This enriches spans with additional attributes before they're exported.

Update your `tracing.py`:

```python
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor, BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from openinference.instrumentation.pydantic_ai import OpenInferenceSpanProcessor
from openinference.instrumentation.pydantic_ai.utils import is_openinference_span

_initialized = False

def init_tracing(
    endpoint: str = "http://127.0.0.1:6006/v1/traces",
    service_name: str = "pydantic-ai-app",
    batch: bool = False,
) -> None:
    """Initialize tracing with OpenInference conventions for Phoenix."""
    global _initialized
    if _initialized:
        return

    resource = Resource.create({"service.name": service_name})
    tracer_provider = TracerProvider(resource=resource)

    # Add OpenInference processor FIRST
    # It enriches spans with OpenInference attributes before export
    # The span_filter ensures only PydanticAI spans are processed
    tracer_provider.add_span_processor(
        OpenInferenceSpanProcessor(span_filter=is_openinference_span)
    )

    # Then add the exporter (SimpleSpanProcessor for dev, BatchSpanProcessor for prod)
    exporter = OTLPSpanExporter(endpoint=endpoint)
    processor = BatchSpanProcessor(exporter) if batch else SimpleSpanProcessor(exporter)
    tracer_provider.add_span_processor(processor)

    trace.set_tracer_provider(tracer_provider)
    _initialized = True
```

**Why does processor order matter?** Span processors run in order. The OpenInference processor must enrich the span *before* the exporter reads it.

**Additional dependency:**
```bash
pip install openinference-instrumentation-pydantic-ai
```

### Adding Session and User Context (OpenInference Only)

OpenInference provides a context manager to attach metadata to traces:

```python
from openinference.instrumentation import using_attributes

async def handle_user_message(user_id: str, session_id: str, message: str):
    with using_attributes(
        session_id=session_id,
        user_id=user_id,
        metadata={"environment": "development"},
    ):
        result = await agent.run(message)
        return result.output
```

This metadata appears in Phoenix and makes it easy to filter traces by user, session, or custom attributes.

---

## Troubleshooting

### Traces not appearing in Phoenix

1. **Endpoint mismatch?** When passing `endpoint` directly to `OTLPSpanExporter()`, use the full path including `/v1/traces`. When using the `OTEL_EXPORTER_OTLP_ENDPOINT` environment variable, use just the base URL—the SDK appends the path automatically.

2. **Is Phoenix running?** Check that http://127.0.0.1:6006 loads in your browser.

3. **Initialization order?** Call `init_tracing()` or `register()` *before* creating any agents or making LLM calls. The TracerProvider must be set globally before instrumentation kicks in.

4. **Missing instrumentation call?** If using Standard OTel (not OpenInference with auto_instrument), ensure you've called `Agent.instrument_all()`.

### Empty or minimal trace data

By default, PydanticAI includes message content in traces. If you're seeing empty content:

```python
from pydantic_ai.models.instrumented import InstrumentationSettings

# Explicitly enable content capture
Agent.instrument_all(InstrumentationSettings(include_content=True))
```

### Traces appearing but not linked together

This usually means the TracerProvider wasn't set before agents were created. Ensure tracing initialization happens at application startup, before any agent code runs.

---

## Summary

| Approach | Dependencies | Semantic Conventions | Phoenix Features | Portability |
|----------|--------------|---------------------|------------------|-------------|
| **Quick Start: OpenInference** | `arize-phoenix-otel`, `openinference-instrumentation-pydantic-ai` | OpenInference | Best (threading, sessions) | Arize ecosystem |
| **Quick Start: Standard OTel** | `arize-phoenix-otel` | OTel GenAI | Good | Any OTel backend |
| **Manual Setup** | `opentelemetry-*` (+ `openinference-*` optionally) | Either | Depends on config | Full control |

**Start with Quick Start: OpenInference** for the best Phoenix experience. Use **Standard OTel** if you need portability. Use **Manual Setup** to learn the internals or customize behavior.

---

## References

- [Arize Phoenix Documentation](https://arize.com/docs/phoenix/)
- [Phoenix OTEL Package](https://github.com/Arize-ai/phoenix/tree/main/packages/phoenix-otel)
- [PydanticAI Instrumentation API](https://ai.pydantic.dev/api/models/instrumented/)
- [OpenTelemetry Python Documentation](https://opentelemetry.io/docs/languages/python/)
- [OpenInference Semantic Conventions](https://arize-ai.github.io/openinference/)
- [OpenInference PydanticAI Instrumentation](https://github.com/Arize-ai/openinference/tree/main/python/instrumentation/openinference-instrumentation-pydantic-ai)
