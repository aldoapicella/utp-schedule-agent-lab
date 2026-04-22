from __future__ import annotations

import re


SECRET_PATTERNS = [
    re.compile(r"(contrase(?:n|ñ)a\s*(?:es|:)\s*)(\S+)", re.IGNORECASE),
    re.compile(r"(password\s*(?:is|:)\s*)(\S+)", re.IGNORECASE),
    re.compile(r"(c[eé]dula\s*(?:es|:)\s*)(\S+)", re.IGNORECASE),
]


def redact_sensitive_text(text: str) -> str:
    redacted = text
    for pattern in SECRET_PATTERNS:
        redacted = pattern.sub(r"\1[REDACTED]", redacted)
    return redacted

