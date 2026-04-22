from __future__ import annotations

import os
import time
import uuid
from dataclasses import asdict, is_dataclass
from pathlib import Path
from typing import Any

from schedule_calculator.adapters.in_memory_repository import InMemoryGroupCatalogRepository
from schedule_calculator.application.scheduler import SchedulerService
from schedule_agent.data.catalog import CatalogStore, default_data_dir
from schedule_agent.human.approval_queue import ApprovalQueue
from schedule_agent.human.escalation_policy import decide_escalation
from schedule_agent.knowledge.retriever import KnowledgeRetriever
from schedule_agent.llm.provider import get_llm_client
from schedule_agent.memory.preference_extractor import PreferenceExtractor
from schedule_agent.memory.session_memory import SessionMemoryStore
from schedule_agent.monitoring.telemetry import TelemetrySession
from schedule_agent.orchestration.planner_executor import PlannerExecutor
from schedule_agent.orchestration.state import AgentState
from schedule_agent.security.input_guard import InputGuard
from schedule_agent.security.tool_permissions import assert_tool_allowed
from schedule_agent.tools.catalog_tools import CatalogTools
from schedule_agent.tools.human_tools import HumanTools
from schedule_agent.tools.policy_tools import PolicyTools
from schedule_agent.tools.registry import ToolRegistry
from schedule_agent.tools.schemas import ToolCallRecord
from schedule_agent.tools.schedule_tools import ScheduleTools


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


class UTPPlanningAgent:
    def __init__(self, data_dir: str | Path | None = None, database_path: str | Path | None = None) -> None:
        self.data_dir = Path(data_dir or default_data_dir())
        self.database_path = Path(database_path or os.getenv("DATABASE_PATH", _repo_root() / "artifacts" / "lab.db"))
        self.trace_dir = Path(os.getenv("TRACE_DIR", _repo_root() / "artifacts" / "traces"))
        self.trace_dir.mkdir(parents=True, exist_ok=True)
        self.catalog = CatalogStore(self.data_dir)
        self.group_repository = InMemoryGroupCatalogRepository.from_json(self.data_dir / "group_catalog.json")
        self.scheduler = SchedulerService(self.group_repository)
        self.memory_store = SessionMemoryStore(self.database_path)
        self.approval_queue = ApprovalQueue(self.database_path)
        self.guard = InputGuard()
        self.preference_extractor = PreferenceExtractor(self.catalog)
        self.retriever = KnowledgeRetriever(_repo_root() / "src" / "schedule_agent" / "knowledge" / "docs")
        self.llm = get_llm_client()
        self.planner = PlannerExecutor()
        self.registry = ToolRegistry()
        self.catalog_tools = CatalogTools(self.catalog, self.group_repository)
        self.schedule_tools = ScheduleTools(self.catalog, self.scheduler)
        self.policy_tools = PolicyTools(self.retriever)
        self.human_tools = HumanTools(self.approval_queue)
        self._register_tools()

    def _register_tools(self) -> None:
        self.registry.register("get_student_profile", self.catalog_tools.get_student_profile)
        self.registry.register("list_available_subjects", self.catalog_tools.list_available_subjects)
        self.registry.register("get_subject_details", self.catalog_tools.get_subject_details)
        self.registry.register("get_available_groups", self.catalog_tools.get_available_groups)
        self.registry.register("check_prerequisites", self.catalog_tools.check_prerequisites)
        self.registry.register("calculate_best_schedule", self.schedule_tools.calculate_best_schedule)
        self.registry.register("validate_schedule", self.schedule_tools.validate_schedule)
        self.registry.register("explain_academic_policy", self.policy_tools.explain_academic_policy)
        self.registry.register("request_human_review", self.human_tools.request_human_review)

    def _call_tool(
        self,
        state: AgentState,
        telemetry: TelemetrySession,
        tool_name: str,
        **kwargs: Any,
    ) -> Any:
        def to_json_safe(value: Any) -> Any:
            if is_dataclass(value):
                return to_json_safe(asdict(value))
            if isinstance(value, dict):
                return {key: to_json_safe(item) for key, item in value.items() if key != "_raw_result"}
            if isinstance(value, (list, tuple)):
                return [to_json_safe(item) for item in value]
            if hasattr(value, "isoformat"):
                try:
                    return value.isoformat()
                except TypeError:
                    return str(value)
            return value if isinstance(value, (str, int, float, bool)) or value is None else str(value)

        assert_tool_allowed(tool_name)
        telemetry.event("tool.called", tool=tool_name, input_summary=to_json_safe(kwargs))
        started = time.perf_counter()
        try:
            tool = self.registry.get(tool_name)
            result = tool(**kwargs)
        except Exception as exc:
            latency_ms = int((time.perf_counter() - started) * 1000)
            telemetry.event("tool.failed", tool=tool_name, latency_ms=latency_ms, error=str(exc))
            record = ToolCallRecord(
                name=tool_name,
                status="failed",
                latency_ms=latency_ms,
                input_summary=to_json_safe(kwargs),
                output_summary={"error": str(exc)},
            )
            state.tool_calls.append(record.to_dict())
            raise
        latency_ms = int((time.perf_counter() - started) * 1000)
        telemetry.event("tool.succeeded", tool=tool_name, latency_ms=latency_ms)
        summary = to_json_safe(result if isinstance(result, dict) else {"result_type": type(result).__name__})
        record = ToolCallRecord(
            name=tool_name,
            status="succeeded",
            latency_ms=latency_ms,
            input_summary=to_json_safe(kwargs),
            output_summary=summary,
        )
        state.tool_calls.append(record.to_dict())
        return result

    def respond(
        self,
        *,
        student_id: str,
        message: str,
        term: str,
        session_id: str | None = None,
        career: str | None = None,
    ) -> dict[str, Any]:
        session_id = session_id or str(uuid.uuid4())
        telemetry = TelemetrySession(self.trace_dir, session_id)
        telemetry.event("agent.started", student_id=student_id, message=message)
        previous_state = self.memory_store.load_state(session_id) or {}
        guard_result = self.guard.inspect(message)
        state = AgentState(session_id=session_id, student_id=student_id, user_message=guard_result.sanitized_message)
        state.warnings.extend(guard_result.warnings)

        state.extracted_preferences = self.preference_extractor.extract(
            guard_result.sanitized_message,
            previous_memory=previous_state.get("memory_snapshot"),
        )
        telemetry.event("preferences.extracted", preferences=state.extracted_preferences)

        state.student_profile = self._call_tool(
            state,
            telemetry,
            "get_student_profile",
            student_id=student_id,
        )
        if state.student_profile is None:
            raise ValueError(f"Unknown student_id '{student_id}'.")

        state.extracted_preferences.setdefault(
            "desired_province",
            state.student_profile.get("current_province", "PANAMÁ"),
        )
        state.extracted_preferences.setdefault(
            "max_credits",
            state.student_profile.get("max_credits"),
        )
        subject_ids = state.extracted_preferences.get("desired_subjects", [])
        if not subject_ids:
            available_subjects = self._call_tool(
                state,
                telemetry,
                "list_available_subjects",
                career_code=career or state.student_profile["career"],
                term=term,
            )
            subject_ids = [
                subject["subject_id"]
                for subject in available_subjects
                if self.group_repository.list_groups_for_subject(subject["subject_id"])
            ][:3]
            state.extracted_preferences["desired_subjects"] = subject_ids

        missing_prereqs = self._call_tool(
            state,
            telemetry,
            "check_prerequisites",
            student_id=student_id,
            subject_ids=subject_ids,
        )

        available_groups = self._call_tool(
            state,
            telemetry,
            "get_available_groups",
            subject_ids=subject_ids,
            province=state.extracted_preferences["desired_province"],
        )
        telemetry.event("groups.loaded", subject_count=len(available_groups))

        state.candidate_schedule = self._call_tool(
            state,
            telemetry,
            "calculate_best_schedule",
            payload={
                "desired_subjects": subject_ids,
                "required_subjects": state.extracted_preferences.get("required_subjects", []),
                "available_start": state.extracted_preferences.get("available_start", "08:00"),
                "available_end": state.extracted_preferences.get("available_end", "22:30"),
                "desired_province": state.extracted_preferences["desired_province"],
                "avoid_days": state.extracted_preferences.get("avoid_days", []),
            },
        )

        state.validation_report = self._call_tool(
            state,
            telemetry,
            "validate_schedule",
            schedule_payload=state.candidate_schedule,
            preferences=state.extracted_preferences,
            missing_prerequisites=missing_prereqs,
        )

        escalation = decide_escalation(
            input_guard_escalate=guard_result.escalate,
            missing_prerequisites=missing_prereqs,
            has_schedule=state.candidate_schedule is not None,
            validation_failures=state.validation_report["hard_constraints"],
        )
        if escalation.required:
            state.human_review = self._call_tool(
                state,
                telemetry,
                "request_human_review",
                reason=escalation.reason or "Manual review required",
                payload={
                    "student_id": student_id,
                    "message": guard_result.sanitized_message,
                    "preferences": state.extracted_preferences,
                    "missing_prerequisites": missing_prereqs,
                },
            )
            telemetry.event("human_review.requested", reason=escalation.reason)

        explanation_lines = [
            f"Materias consideradas: {', '.join(subject_ids)}.",
            f"Provincia preferida: {state.extracted_preferences['desired_province']}.",
            f"Disponibilidad: {state.extracted_preferences.get('available_start')} a {state.extracted_preferences.get('available_end')}.",
        ]
        if state.validation_report["warnings"]:
            explanation_lines.extend(state.validation_report["warnings"])
        if missing_prereqs:
            explanation_lines.append(f"Prerrequisitos faltantes: {missing_prereqs}.")
        if guard_result.escalate:
            policy = self._call_tool(
                state,
                telemetry,
                "explain_academic_policy",
                topic="lab_domain_rules",
            )
            explanation_lines.append(policy["explanation"].splitlines()[0])

        llm_output = self.llm.compose_response(
            {
                "recommended_schedule": (
                    state.candidate_schedule["chosen_enrollments"] if state.candidate_schedule else []
                ),
                "explanation_lines": explanation_lines,
                "human_review": state.human_review,
            }
        )

        memory_snapshot = {
            "desired_subjects": subject_ids,
            "required_subjects": state.extracted_preferences.get("required_subjects", []),
            "avoid_days": state.extracted_preferences.get("avoid_days", []),
            "available_start": state.extracted_preferences.get("available_start"),
            "available_end": state.extracted_preferences.get("available_end"),
            "desired_province": state.extracted_preferences.get("desired_province"),
            "preferred_shift": state.extracted_preferences.get("preferred_shift"),
            "max_credits": state.extracted_preferences.get("max_credits"),
        }
        self.memory_store.save_state(
            session_id,
            student_id,
            {
                "memory_snapshot": memory_snapshot,
                "student_profile": state.student_profile,
                "last_validation_report": state.validation_report,
                "last_human_review": state.human_review,
            },
        )
        telemetry.event("agent.completed", escalated=bool(state.human_review))

        recommended_schedule = None
        if state.candidate_schedule:
            recommended_schedule = {
                key: value for key, value in state.candidate_schedule.items() if key != "_raw_result"
            }

        return {
            "session_id": session_id,
            "assistant_message": llm_output.assistant_message,
            "recommended_schedule": recommended_schedule,
            "explanation": llm_output.explanation,
            "tool_calls": state.tool_calls,
            "memory_snapshot": memory_snapshot,
            "validation_report": state.validation_report,
            "human_review": state.human_review,
            "warnings": state.warnings,
            "plan": self.planner.get_plan(),
        }
