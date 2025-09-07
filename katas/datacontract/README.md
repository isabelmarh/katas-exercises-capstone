# Data Contract Generation Kata

## Goal

The goal of this kata is to build an AI agent that converts unstructured text or documents into valid data contracts following the [Data Contract Specification](https://github.com/datacontract/datacontract-specification).

## Challenge

Your agent must:
- Parse unstructured documentation, requirements, or descriptions
- Extract data structure and schema information
- Generate valid YAML following the Data Contract Specification format
- Include appropriate metadata, quality checks, and governance information
- Handle PII identification and data classification
- Define service level agreements and terms of use

## Key Components to Generate

A complete data contract should include:

- **dataContractSpecification**: Version identifier (e.g., "1.1.0")
- **info**: Title, version, description, owner, contact details
- **servers**: Data location, format, and connection details
- **terms**: Usage rights, limitations, billing, notice periods
- **models**: Data schema with fields, types, constraints, and relationships
- **definitions**: Reusable field definitions and data types
- **servicelevels**: Availability, retention, freshness, latency requirements
- **quality**: Data quality checks and validation rules

## Steps

1. Review the [Data Contract Specification](https://datacontract.com/) and example contracts
2. Examine the `evals.yaml` file to understand the test cases
3. **Hint**: Use `datamodel-code-generator` to create Pydantic models from the JSON schema:
   ```bash
   pip install datamodel-code-generator
   datamodel-codegen --url https://raw.githubusercontent.com/datacontract/datacontract-specification/main/datacontract.schema.json --output datacontract_models.py
   ```
4. Implement the agent in `main.py` following the function signature
5. Test your implementation against various types of unstructured input
6. Ensure generated contracts are valid and comprehensive

## Example Inputs

Your agent should handle various formats:
- Informal documentation: "We have customer data with emails, order amounts..."
- Database schemas: SQL DDL statements or table descriptions
- API documentation: REST API specifications or field descriptions
- Business requirements: Stakeholder descriptions of data needs
- Existing data samples: CSV headers or JSON examples

## Resources

- [Data Contract Specification](https://datacontract.com/)
- [Example Orders Contract](https://datacontract.com/examples/orders-latest/datacontract.yaml)
- [datamodel-code-generator](https://github.com/koxudaxi/datamodel-code-generator)
- [Data Contract CLI](https://cli.datacontract.com/)

Start implementing in `main.py` and validate your contracts!
