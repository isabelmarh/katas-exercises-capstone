import re
from pydantic import BaseModel, Field
from opentelemetry import trace

tracer = trace.get_tracer(__name__)


class GuardrailResult(BaseModel):
    passed: bool
    reason: str | None = None
    sanitized_input: str | None = None


class InputGuardrails:
    PII_PATTERNS = [
        (r"\b\d{3}-\d{2}-\d{4}\b", "SSN"),
        (r"\b\d{16}\b", "Credit Card"),
        (r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", "Email"),
    ]

    PROMPT_INJECTION_PATTERNS = [
        r"ignore previous instructions",
        r"disregard all",
        r"new instructions",
        r"system:",
    ]

    @tracer.start_as_current_span("check_guardrails")
    def validate_input(self, user_input: str) -> GuardrailResult:
        if len(user_input) > 2000:
            return GuardrailResult(
                passed=False, reason="Input exceeds maximum length of 2000 characters"
            )

        for pattern, pii_type in self.PII_PATTERNS:
            if re.search(pattern, user_input):
                return GuardrailResult(
                    passed=False, reason=f"Potential PII detected: {pii_type}"
                )

        lower_input = user_input.lower()
        for pattern in self.PROMPT_INJECTION_PATTERNS:
            if pattern in lower_input:
                return GuardrailResult(
                    passed=False, reason="Potential prompt injection detected"
                )

        return GuardrailResult(passed=True, sanitized_input=user_input.strip())
