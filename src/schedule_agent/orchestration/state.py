from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class AgentState:
    student_id: str
    user_message: str
    extracted_preferences: dict[str, Any] = field(default_factory=dict)
    student_profile: dict[str, Any] | None = None
    tool_calls: list[dict[str, Any]] = field(default_factory=list)
    candidate_schedule: dict[str, Any] | None = None
    validation_report: dict[str, Any] | None = None
    warnings: list[str] = field(default_factory=list)
    human_review: dict[str, Any] | None = None
