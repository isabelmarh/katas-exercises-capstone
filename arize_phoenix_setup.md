# Adding Arize Phoenix to a PydanticAI Project

## Introduction

This guide walks you through setting up **Arize Phoenix**, an open-source AI observability platform, to monitor and debug your PydanticAI agents. By the end, you'll have traces flowing from your agents into Phoenix for visualization and debugging.

We present two approaches:
- **Standard OTel** (recommended) — Simple setup, portable to any OpenTelemetry backend
- **Manual + OpenInference** — More code, but richer Phoenix visualizations

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

## Running Phoenix

Regardless of which approach you choose, you need Phoenix running to receive traces.

**Recommended option** (using uvx):
We don't actually need Phoenix installed into our agent's virtual environment; we just need to it to run as a standalone service, which means using `uv`'s uvx command is perfect. It will lauch the provided command in a standalone virtual environment, which it creates automatically for you. 

```bash
uvx arize-phoenix serve
```

**Alternative** (using pip):
If for some reason you want to manually install Pheonix into a specific virtual environment, you can do the following: 

```bash
uv pip install arize-phoenix
uv run arize-phoenix serve
```

**Alternative** (using Docker):
If you have a docker service running on your machine, you can also launch Phoenix like so:

```bash
docker run -d -p 6006:6006 arizephoenix/phoenix:latest
```

### Accessing Phoenix

After completing one of the above steps, Phoenix will be available at **http://127.0.0.1:6006**. Open this in your browser to see the UI.

---

## Option 1: Standard OTel (Recommended)

This approach uses industry-standard OpenTelemetry semantic conventions (OTel GenAI). Traces work with Phoenix and any other OTel-compatible backend (Jaeger, Datadog, Honeycomb, etc.).

### Install Dependencies

```bash
uv pip install arize-phoenix-otel
```

### Configure Tracing

```python
from phoenix.otel import register
from pydantic_ai import Agent

register(
    project_name="my-app",
    endpoint="http://127.0.0.1:6006/v1/traces",
)
Agent.instrument_all()
```

Here's what's happening:

- **`register()`** sets up a TracerProvider, SpanProcessor, and Exporter with sensible defaults
- **`project_name`** labels your traces in Phoenix for easy filtering
- **`endpoint`** specifies the Phoenix OTLP HTTP endpoint (include `/v1/traces` path)
- **`Agent.instrument_all()`** enables PydanticAI to emit traces

### Complete Example

```python
import asyncio
from phoenix.otel import register
from pydantic_ai import Agent

# Configure tracing (must be called before creating agents)
register(
    project_name="weather-app",
    endpoint="http://127.0.0.1:6006/v1/traces",
)
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
    endpoint="http://127.0.0.1:6006/v1/traces",
    batch=True,  # Batch spans for better performance (slight delay)
)
```

You can also configure the endpoint via environment variable (note: use the base URL without `/v1/traces`—the SDK appends the path automatically):
```bash
export OTEL_EXPORTER_OTLP_ENDPOINT=http://127.0.0.1:6006
```

---

## Option 2: Manual + OpenInference

This approach gives you the richest Phoenix experience with OpenInference semantic conventions. It requires manual TracerProvider setup but provides enhanced visualizations, conversation threading, and session attribution.

### Install Dependencies

```bash
uv pip install opentelemetry-api opentelemetry-sdk opentelemetry-exporter-otlp openinference-instrumentation-pydantic-ai
```

### Complete Example

```python
import asyncio
from openinference.instrumentation.pydantic_ai import OpenInferenceSpanProcessor
from openinference.semconv.resource import ResourceAttributes
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from pydantic_ai import Agent


def init_telemetry(project_name: str | None = None) -> None:
    """Initialize OpenTelemetry tracing with OpenInference for Phoenix."""
    # Create and register a TracerProvider (project_name appears in Phoenix UI)
    resource = Resource.create({ResourceAttributes.PROJECT_NAME: project_name}) if project_name else None
    tracer_provider = TracerProvider(resource=resource)
    trace.set_tracer_provider(tracer_provider)

    # Enrich spans with OpenInference attributes (must be added before exporter)
    tracer_provider.add_span_processor(OpenInferenceSpanProcessor())

    # Export spans to Phoenix
    tracer_provider.add_span_processor(SimpleSpanProcessor(
        OTLPSpanExporter(endpoint="http://127.0.0.1:6006/v1/traces")
    ))

    # Enable PydanticAI instrumentation
    Agent.instrument_all()


init_telemetry(project_name="weather-app")

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

**Key points:**
- The `project_name` parameter sets the Phoenix project name (via OpenInference `ResourceAttributes.PROJECT_NAME`)
- Add `OpenInferenceSpanProcessor` *before* `SimpleSpanProcessor` — processors run in order, so enrichment must happen before export
- Use `BatchSpanProcessor` instead of `SimpleSpanProcessor` in production for better performance (spans are buffered, so there's a slight delay before they appear)

### Graceful Shutdown (Production)

When using `BatchSpanProcessor`, spans are buffered in memory. If your application exits abruptly, buffered spans may be lost. To ensure all traces are exported before shutdown:

```python
from opentelemetry import trace

# At application shutdown (e.g., in a finally block or signal handler)
tracer_provider = trace.get_tracer_provider()
if hasattr(tracer_provider, 'shutdown'):
    tracer_provider.shutdown()  # Flushes pending spans and releases resources
```

This isn't needed with `SimpleSpanProcessor` since spans are exported immediately.

### Adding Session and User Context

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

1. **Endpoint mismatch?** When passing `endpoint` directly to `OTLPSpanExporter()` or `register()`, use the full path including `/v1/traces`. When using the `OTEL_EXPORTER_OTLP_ENDPOINT` environment variable, use just the base URL—the SDK appends the path automatically.

2. **Is Phoenix running?** Check that http://127.0.0.1:6006 loads in your browser.

3. **Initialization order?** Call `init_tracing()` or `register()` *before* creating any agents or making LLM calls. The TracerProvider must be set globally before instrumentation kicks in.

4. **Missing instrumentation call?** Ensure you've called `Agent.instrument_all()`.

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
| **Option 1: Standard OTel** | `arize-phoenix-otel` | OTel GenAI | Good | Any OTel backend |
| **Option 2: Manual + OpenInference** | `opentelemetry-*`, `openinference-instrumentation-pydantic-ai` | OpenInference | Best (threading, sessions) | Arize ecosystem |

**Start with Option 1 (Standard OTel)** for simplicity and portability. Use **Option 2 (Manual + OpenInference)** if you need richer Phoenix visualizations and are committed to the Arize ecosystem.

---

## References

- [Arize Phoenix Documentation](https://arize.com/docs/phoenix/)
- [Phoenix OTEL Package](https://github.com/Arize-ai/phoenix/tree/main/packages/phoenix-otel)
- [PydanticAI Instrumentation API](https://ai.pydantic.dev/api/models/instrumented/)
- [OpenTelemetry Python Documentation](https://opentelemetry.io/docs/languages/python/)
- [OpenInference Semantic Conventions](https://arize-ai.github.io/openinference/)
- [OpenInference PydanticAI Instrumentation](https://github.com/Arize-ai/openinference/tree/main/python/instrumentation/openinference-instrumentation-pydantic-ai)
