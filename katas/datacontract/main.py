from __future__ import annotations

from typing import Any

from pydantic_ai import Agent
from pydantic_evals import Case, Dataset
from pydantic_evals.evaluators import EqualsExpected, LLMJudge

agent = Agent(
    model="anthropic:claude-sonnet-4-5",
    instructions="""You are a Data Contract Generation Agent following the Data Contract Specification 1.1.0.

You MUST output pure YAML only - no markdown, no code fences, no backticks, no ```yaml backticks, no explanation.

STRUCTURE:
- dataContractSpecification: 1.1.0
- id: kebab-case identifier
- info: title, version (1.0.0), description, owner (only if owner mentioned)
- terms: usage, limitations (only if usage/limitations mentioned)
- models: table definitions
- servicelevels: only if SLA info mentioned

STRICT RULES:
1. Field types: "text" (NEVER "string"), "integer", "decimal", "timestamp", "boolean"
2. enum: ALWAYS inline: enum: [val1, val2, val3]
3. Key is "servicelevels" (one word, lowercase)
4. NEVER add "availability" under servicelevels. Only: freshness, retention, frequency
5. "available within X hours" → freshness with threshold, NOT availability
6. Each servicelevel entry: description as first property
7. Only include sections/properties that are relevant to the input
8. You MUST output pure YAML only - no markdown, no code fences, no backticks, no ```yaml backticks, no explanation.

FOR UNSTRUCTURED TEXT INPUT (like descriptions of databases):
- No model-level description
- Field property order: type, format, required, unique, primaryKey, pii, description, enum
- Field names: snake_case from input words ("Customer email address" → customer_email_address, "Total amount in cents" → total_amount)
- models key: short plural noun ("orders" not "customer_orders")
- Descriptions: short and direct
  - ID fields: "Unique identifier"
  - PII fields: exact input text e.g. "Customer email address (contains PII)"
  - Timestamps: parenthetical from input e.g. "When order was placed"
  - Amounts: "Total amount in cents"
  - Status fields: "Order status"
- Service level descriptions: exact sentence from input
- terms: exact phrases from input

FOR SQL DDL INPUT:
- Include model-level description (e.g., "Products catalog for e-commerce website")
- Map SQL types: VARCHAR → text, SERIAL/INTEGER → integer, DECIMAL(p,s) → decimal with precision/scale, TIMESTAMP → timestamp, TEXT → text
- Include maxLength for VARCHAR(n) fields
- Include precision and scale for DECIMAL(p,s) fields
- Field property order: type, maxLength (if any), precision (if any), scale (if any), required, unique, primaryKey, description, quality (if any), references (if any)
- NOT NULL → required: true
- UNIQUE → unique: true
- PRIMARY KEY → primaryKey: true, required: true, unique: true
- REFERENCES table(col) → references: table.col
- CHECK constraints → quality section on the field:
    quality:
      - type: sql
        description: human readable description of check
        query: SELECT * FROM table WHERE violation_condition
        mustBeEmpty: true
- Field descriptions: short generic labels ("Product identifier", "Stock keeping unit", "Product name", "Product description", "Product price", "Category reference", "Record creation timestamp")
- SERIAL PRIMARY KEY → type: integer (not text)
- CDC/real-time → frequency type: streaming (no interval)
- No terms section unless explicitly mentioned
- info: no owner unless mentioned

FOR CSV HEADER INPUT:
- Include model-level description (e.g., "User data")
- Infer field types: id → text, name → text, email → text with format: email and pii: true, age → integer, country → text
- Field property order: type, format, required, unique, primaryKey, pii, description
- id field: required: true, primaryKey: true
- name field: required: true
- email field: required: true, pii: true, format: email
- Other fields: no required
- Descriptions: "User identifier", "User name", "User email address", "User age", "User country"
- No terms, no servicelevels unless mentioned
- info: no owner unless mentioned"""
)

def main(unstructured_input: str) -> str:
    """
    Data Contract Generation Agent

    This function should analyze unstructured text or documents and generate
    a valid data contract YAML following the Data Contract Specification.

    The agent should extract:
    - Data structure and schema information
    - Field names, types, and constraints
    - Business rules and quality requirements
    - Metadata like descriptions, owners, and terms
    - Service level agreements (SLAs)
    - Data governance requirements (PII, classification)

    Key sections to generate:
    - dataContractSpecification: Version (e.g., "1.1.0")
    - id: Unique identifier for the contract
    - info: Title, version, description, owner, contact
    - servers: Data location and format details
    - terms: Usage rights, limitations, billing
    - models: Data schema with fields, types, constraints
    - definitions: Reusable field definitions
    - servicelevels: Availability, retention, freshness, etc.
    - quality: Data quality checks and rules

    Tips:
    - Use datamodel-code-generator to create Pydantic models from the JSON schema
    - Follow the specification at: https://github.com/datacontract/datacontract-specification
    - Include examples and quality checks where possible
    - Consider PII and data classification requirements
    - Add meaningful descriptions and business context

    Args:
        unstructured_input: Raw text, documentation, or description of data requirements

    Returns:
        Valid datacontract YAML string conforming to the Data Contract Specification
    """
    response = agent.run_sync(unstructured_input).output
    # Strip markdown code fences if the LLM wraps output in them
    result = response.strip()
    if result.startswith("```"):
        result = result.split("\n", 1)[1]  # remove first line (```yaml)
    if result.endswith("```"):
        result = result.rsplit("```", 1)[0]  # remove trailing ```
    return result.strip()


# Evaluation dataset
datacontract_dataset = Dataset[str, str, Any](
    cases=[
        Case(
            name="customer-orders-basic",
            inputs="""We have a customer orders database with the following information:
- Order ID (unique identifier, UUID format)
- Customer email address (contains PII)
- Order timestamp (when order was placed)
- Total amount in cents (integer)
- Order status (pending, completed, cancelled)

Data is updated daily and should be available within 24 hours.
Used for analytics and reporting. No real-time requirements.
Data retention is 2 years. Owned by the checkout team.""",
            expected_output="""dataContractSpecification: 1.1.0
id: customer-orders
info:
  title: Customer Orders
  version: 1.0.0
  description: Customer orders database for analytics and reporting
  owner: checkout team
terms:
  usage: Used for analytics and reporting
  # limitations: No real-time requirements
models:
  orders:
    type: table
    fields:
      order_id:
        type: text
        format: uuid
        required: true
        unique: true
        primaryKey: true
        description: Unique identifier
      customer_email_address:
        type: text
        format: email
        required: true
        pii: true
        description: Customer email address (contains PII)
      order_timestamp:
        type: timestamp
        required: true
        description: When order was placed
      total_amount:
        type: integer
        required: true
        description: Total amount in cents
      order_status:
        type: text
        required: true
        description: Order status
        enum: [pending, completed, cancelled]
servicelevels:
  freshness:
    description: Data should be available within 24 hours
    threshold: 24h
  retention:
    description: Data retention is 2 years
    period: P2Y
  frequency:
    description: Data is updated daily
    type: batch
    interval: daily""",
            evaluators=(
                LLMJudge(
                    model="anthropic:claude-sonnet-4-5",
                    rubric=(
                        "Output must be valid YAML with dataContractSpecification: 1.1.0. "
                        "Must have id: customer-orders, info with title 'Customer Orders', version 1.0.0, owner 'checkout team'. "
                        "Must have terms with usage and limitations. "
                        "Models must have 'orders' table with fields: order_id (text, uuid, primaryKey), "
                        "customer_email_address (text, email, pii), order_timestamp (timestamp), "
                        "total_amount (integer), order_status (text, enum with pending/completed/cancelled). "
                        "Must have servicelevels with freshness (24h), retention (P2Y), frequency (batch, daily). "
                        "Field types must use 'text' not 'string'."
                    ),
                ),
            ),
        ),
        Case(
            name="sql-ddl-schema",
            inputs="""CREATE TABLE products (
    product_id SERIAL PRIMARY KEY,
    sku VARCHAR(50) NOT NULL UNIQUE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    price DECIMAL(10,2) NOT NULL CHECK (price > 0),
    category_id INTEGER REFERENCES categories(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

Table is used for e-commerce catalog.
Updated in real-time via CDC from production database.
Critical for website functionality.""",
            expected_output="""dataContractSpecification: 1.1.0
id: products-catalog
info:
  title: Products Catalog
  version: 1.0.0
  description: E-commerce catalog products table
models:
  products:
    type: table
    description: Products catalog for e-commerce website
    fields:
      product_id:
        type: integer
        required: true
        unique: true
        primaryKey: true
        description: Product identifier
      sku:
        type: text
        maxLength: 50
        required: true
        unique: true
        description: Stock keeping unit
      name:
        type: text
        maxLength: 255
        required: true
        description: Product name
      description:
        type: text
        description: Product description
      price:
        type: decimal
        precision: 10
        scale: 2
        required: true
        description: Product price
        quality:
          - type: sql
            description: Price must be greater than 0
            query: SELECT * FROM products WHERE price <= 0
            mustBeEmpty: true
      category_id:
        type: integer
        description: Category reference
        references: categories.id
      created_at:
        type: timestamp
        required: true
        description: Record creation timestamp
      updated_at:
        type: timestamp
        required: true
        description: Record update timestamp
servicelevels:
  frequency:
    description: Updated in real-time via CDC from production database
    type: streaming""",
            evaluators=(
                LLMJudge(
                    model="anthropic:claude-sonnet-4-5",
                    rubric=(
                        "Output must be valid YAML with dataContractSpecification: 1.1.0. "
                        "Must have id: products-catalog, title as 'Products Catalog', description as 'E-commerce catalog products table'. "
                        "Models must have 'products' table with model-level description. "
                        "Fields: product_id (integer, primaryKey), sku (text, maxLength 50, unique), "
                        "name (text, maxLength 255), description (text), "
                        "price (decimal, precision 10, scale 2, with quality check for price > 0), "
                        "category_id (integer, references categories.id), "
                        "created_at (timestamp), updated_at (timestamp). "
                        "Must have servicelevels with frequency type: streaming. "
                        "Field types must use 'text' not 'string'."
                    ),
                ),
            ),
        ),
        Case(
            name="simple-csv-headers",
            inputs="""Simple CSV file with headers:
id,name,email,age,country

Basic user data export""",
            expected_output="""dataContractSpecification: 1.1.0
id: user-data-export
info:
  title: User Data Export
  version: 1.0.0
  description: Basic user data export from CSV
models:
  users:
    type: table
    description: User data
    fields:
      id:
        type: text
        required: true
        primaryKey: true
        description: User identifier
      name:
        type: text
        required: true
        description: User name
      email:
        type: text
        format: email
        required: true
        pii: true
        description: User email address
      age:
        type: integer
        description: User age
      country:
        type: text
        description: User country""",
            evaluators=(
                LLMJudge(
                    model="anthropic:claude-sonnet-4-5",
                    rubric=(
                        "Output must be valid YAML with dataContractSpecification: 1.1.0. "
                        "Must have id: user-data-export, info with title 'User Data Export', "
                        "description about user data export from CSV. "
                        "Models must have 'users' table with model-level description. "
                        "Fields: id (text, primaryKey), name (text, required), "
                        "email (text, format email, pii true), age (integer), country (text). "
                        "No terms or servicelevels sections. "
                        "Field types must use 'text' not 'string'."
                    ),
                ),
            ),
        ),
    ],
    evaluators=[],
)


if __name__ == "__main__":
    report = datacontract_dataset.evaluate_sync(main)
    report.print()
