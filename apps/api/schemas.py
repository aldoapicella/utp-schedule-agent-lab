from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class AgentChatRequest(BaseModel):
    session_id: str | None = None
    student_id: str
    message: str
    term: str
    career: str | None = None


class ToolCallRecordModel(BaseModel):
    name: str
    status: str
    latency_ms: int
    input_summary: dict[str, Any]
    output_summary: dict[str, Any]


class ValidationReportModel(BaseModel):
    hard_constraints: dict[str, bool]
    warnings: list[str]
    metrics: dict[str, Any] = Field(default_factory=dict)


class HumanReviewTicketModel(BaseModel):
    status: str
    reason: str
    assigned_role: str
    ticket_id: str | None = None
    payload: dict[str, Any] = Field(default_factory=dict)


class AgentChatResponse(BaseModel):
    session_id: str
    assistant_message: str
    recommended_schedule: dict[str, Any] | None
    explanation: list[str]
    tool_calls: list[ToolCallRecordModel]
    memory_snapshot: dict[str, Any]
    validation_report: ValidationReportModel
    human_review: HumanReviewTicketModel | None = None
    warnings: list[str] = Field(default_factory=list)
    plan: list[str] = Field(default_factory=list)


class SessionStateResponse(BaseModel):
    session_id: str
    state: dict[str, Any] | None


class HumanReviewRequest(BaseModel):
    reason: str
    payload: dict[str, Any]

