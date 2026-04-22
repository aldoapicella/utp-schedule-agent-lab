from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class EscalationDecision:
    required: bool
    reason: str | None = None


def decide_escalation(
    *,
    input_guard_escalate: bool,
    missing_prerequisites: dict[str, list[str]],
    has_schedule: bool,
    validation_failures: dict[str, bool],
) -> EscalationDecision:
    if input_guard_escalate:
        return EscalationDecision(True, "Unsafe request or policy bypass attempt")
    if missing_prerequisites:
        return EscalationDecision(True, "Missing prerequisites")
    failing = [name for name, passed in validation_failures.items() if not passed]
    if failing or not has_schedule:
        return EscalationDecision(True, "No valid schedule satisfies the academic constraints")
    return EscalationDecision(False)

