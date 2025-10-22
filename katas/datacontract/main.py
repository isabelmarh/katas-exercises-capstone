from __future__ import annotations

from typing import Any

from pydantic_ai import Agent
from pydantic_evals import Case, Dataset
from pydantic_evals.evaluators import EqualsExpected

from open_data_contract import OpenDataContractStandardOdcs


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
    agent = Agent(
        model="google-gla:gemini-2.5-pro", output_type=OpenDataContractStandardOdcs
    )
    response = agent.run_sync(unstructured_input).output

    return str(response)


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
  limitations: No real-time requirements
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
            evaluators=(EqualsExpected(),),
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
            evaluators=(EqualsExpected(),),
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
            evaluators=(EqualsExpected(),),
        ),
    ],
    evaluators=[],
)


if __name__ == "__main__":
    report = datacontract_dataset.evaluate_sync(main)
    report.print()
