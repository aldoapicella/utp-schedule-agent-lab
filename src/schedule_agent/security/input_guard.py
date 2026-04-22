from __future__ import annotations

from dataclasses import dataclass, field

from schedule_agent.security.pii_redaction import redact_sensitive_text
from schedule_agent.security.prompt_injection_tests import is_prompt_injection_attempt


@dataclass(slots=True)
class InputGuardResult:
    sanitized_message: str
    warnings: list[str] = field(default_factory=list)
    escalate: bool = False


class InputGuard:
    def inspect(self, message: str) -> InputGuardResult:
        sanitized_message = redact_sensitive_text(message)
        warnings: list[str] = []
        escalate = False

        if sanitized_message != message:
            warnings.append("Sensitive credentials were redacted and will not be stored.")
        if is_prompt_injection_attempt(message):
            warnings.append("Potential prompt injection or policy bypass attempt detected.")
            escalate = True
        return InputGuardResult(
            sanitized_message=sanitized_message,
            warnings=warnings,
            escalate=escalate,
        )

