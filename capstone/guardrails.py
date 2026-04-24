import re


EMAIL_RE = re.compile(r"\b[\w.+-]+@[\w-]+\.[\w.-]+\b")
PHONE_RE = re.compile(r"\+?\d[\d\s().-]{7,}\d")


def redact_pii(text: str) -> str:
    """Redact obvious PII before saving user content to memory."""
    text = EMAIL_RE.sub("[REDACTED_EMAIL]", text)
    text = PHONE_RE.sub("[REDACTED_PHONE]", text)
    return text
