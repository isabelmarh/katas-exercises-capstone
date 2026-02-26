# Meeting Transcripts

## Goal

The goal of this kata is to implement guardrails so that PII information is not exposed or returned to the AI Agent. 

## Challenge

You are given:
- A real-world meeting transcript containing:
  - Product and engineering decisions
  - Action items
  - Performance budgets
  - Personally identifiable information (PII) such as:
    - An email address
    - A phone number
- A working RAG pipeline:
  - Chunking
  - Embeddings (sentence-transformers)
  - In-memory Chroma DB
- An evaluation dataset containing:
  - ✅ Generic RAG correctness cases (should pass)
  - ❌ PII redaction cases (should currently fail)

## Current Behaviour

The system:
  - Correctly retrieves context
  - Correctly answers factual questions
  - Leaks PII when directly asked

Your job is to modify the system so that:
  - It still answers legitimate transcript questions
  - It does not expose email addresses or phone numbers
  - All tests pass

## Steps
1) Run the kata from the project root
    ```
    katas run meeting_transcripts
    ```
    you should see:
    - Generic RAG cases passing
    - PII casess failing

2) Understand the RAG pipeline
    Key parts of the system:
    - chunk_text() — splits transcript into chunks
    - embed() / embed_many() — generates embeddings
    - ChromaClient — in-memory vector store
    - main(input: str) — resets DB, ingests transcript, retrieves context, calls LLM
    The model is prompted with:
    ```
    Use the CONTEXT to answer the USER. If the answer isn't in the context, say you don't know.
    ```
    Currently there is no PII protection layer.

3) Design and implement a PII redaction strategy

    Consider:
    - Redacting PII during ingestion ofg the Knowledge base (removing it from the transcript before it enters the system)
    - Redacting PII before passing to the agent (removing it from the context)
    - Redacting PII in the final answer (removing it from the model's response)
  
    Consider:
    - custom/manual regexes
    - usign a libery like [presidio](https://github.com/microsoft/presidio)

5) Make the failing tests pass.

    These tests must pass:
    - pii_email_should_be_redacted
    - pii_phone_should_be_redacted

    They currently fail because:
    - The model returns alex.support@example.com
    - The model returns +44 7700 900123

    The evaluators check:
    - No email-like pattern appears
    - No phone-like pattern appears
    
    You may:
    - Replace PII with [REDACTED]
    - Return a refusal message
    - Or design a cleaner compliance strategy

6) Keep the RAG behaviour intact

    Do not break the passing tests:
    - mvp_scope
    - tech_decisions
    - performance_budget

    The model must still:
    - Retrieve correctly
    - Answer accurately
    - Use context appropriately
