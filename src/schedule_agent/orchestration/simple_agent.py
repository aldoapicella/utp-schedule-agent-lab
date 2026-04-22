from __future__ import annotations

from dataclasses import asdict, is_dataclass
import json
import os
import time
import uuid
from pathlib import Path

from schedule_calculator.adapters.in_memory_repository import InMemoryGroupCatalogRepository
from schedule_calculator.application.scheduler import SchedulerService
from schedule_agent.data.catalog import CatalogStore, default_data_dir
from schedule_agent.memory.preference_extractor import PreferenceExtractor
from schedule_agent.memory.session_memory import SessionMemoryStore
from schedule_agent.monitoring.telemetry import TelemetrySession
from schedule_agent.orchestration.planner_executor import PlannerExecutor
from schedule_agent.orchestration.state import AgentState
from schedule_agent.tools.catalog_tools import CatalogTools
from schedule_agent.tools.schedule_tools import ScheduleTools
from schedule_agent.tools.schemas import ToolCallRecord


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
        self.catalog_tools = CatalogTools(self.catalog, self.group_repository)
        self.schedule_tools = ScheduleTools(self.catalog, self.scheduler)
        self.planner = PlannerExecutor()
        self.preference_extractor = PreferenceExtractor(self.catalog)
        self.memory_store = SessionMemoryStore(self.database_path)

    def _record(self, name: str, input_summary: dict, output_summary: dict, latency_ms: int) -> dict:
        return ToolCallRecord(
            name=name,
            status="succeeded",
            latency_ms=latency_ms,
            input_summary=input_summary,
            output_summary=output_summary,
        ).to_dict()

    def _to_json_safe(self, value):
        if is_dataclass(value):
            return self._to_json_safe(asdict(value))
        if isinstance(value, dict):
            return {
                key: self._to_json_safe(item)
                for key, item in value.items()
                if key != "_raw_result"
            }
        if isinstance(value, (list, tuple)):
            return [self._to_json_safe(item) for item in value]
        if hasattr(value, "isoformat"):
            try:
                return value.isoformat()
            except TypeError:
                return str(value)
        if isinstance(value, (str, int, float, bool)) or value is None:
            return value
        return str(value)

    def _call_tool(self, telemetry: TelemetrySession, state: AgentState, name: str, fn, **kwargs):
        telemetry.event("tool.called", tool=name, input_summary=self._to_json_safe(kwargs))
        started = time.perf_counter()
        result = fn(**kwargs)
        latency_ms = int((time.perf_counter() - started) * 1000)
        telemetry.event("tool.succeeded", tool=name, latency_ms=latency_ms)
        summary = self._to_json_safe(result if isinstance(result, dict) else {"result": result})
        state.tool_calls.append(self._record(name, self._to_json_safe(kwargs), summary, latency_ms))
        return result

    def respond(
        self,
        *,
        student_id: str,
        message: str,
        term: str,
        career: str | None = None,
        session_id: str | None = None,
    ) -> dict:
        session_id = session_id or str(uuid.uuid4())
        telemetry = TelemetrySession(self.trace_dir, session_id)
        telemetry.event("agent.started", student_id=student_id, message=message)

        previous_state = self.memory_store.load_state(session_id) or {}
        state = AgentState(student_id=student_id, user_message=message)
        state.student_profile = self._call_tool(
            telemetry,
            state,
            "get_student_profile",
            self.catalog_tools.get_student_profile,
            student_id=student_id,
        )
        if state.student_profile is None:
            raise ValueError(f"Unknown student_id '{student_id}'.")

        state.extracted_preferences = self.preference_extractor.extract(
            message,
            previous_memory=previous_state.get("memory_snapshot"),
        )
        state.extracted_preferences.setdefault("desired_province", state.student_profile["current_province"])
        state.extracted_preferences.setdefault("available_start", "08:00")
        state.extracted_preferences.setdefault("available_end", "22:30")
        state.extracted_preferences.setdefault("required_subjects", [])
        state.extracted_preferences.setdefault("desired_subjects", [])
        telemetry.event("preferences.extracted", preferences=state.extracted_preferences)

        if not state.extracted_preferences["desired_subjects"]:
            available = self._call_tool(
                telemetry,
                state,
                "list_available_subjects",
                self.catalog_tools.list_available_subjects,
                career_code=career or state.student_profile["career"],
                term=term,
            )
            state.extracted_preferences["desired_subjects"] = [subject["subject_id"] for subject in available[:3]]

        missing_prerequisites = self._call_tool(
            telemetry,
            state,
            "check_prerequisites",
            self.catalog_tools.check_prerequisites,
            student_id=student_id,
            subject_ids=state.extracted_preferences["desired_subjects"],
        )

        available_groups = self._call_tool(
            telemetry,
            state,
            "get_available_groups",
            self.catalog_tools.get_available_groups,
            subject_ids=state.extracted_preferences["desired_subjects"],
            province=state.extracted_preferences["desired_province"],
        )
        telemetry.event("groups.loaded", subject_count=len(available_groups))

        state.candidate_schedule = self._call_tool(
            telemetry,
            state,
            "calculate_best_schedule",
            self.schedule_tools.calculate_best_schedule,
            payload=state.extracted_preferences,
        )

        state.validation_report = self._call_tool(
            telemetry,
            state,
            "validate_schedule",
            self.schedule_tools.validate_schedule,
            schedule_payload=state.candidate_schedule,
            preferences=state.extracted_preferences,
            missing_prerequisites=missing_prerequisites,
        )

        human_review = None
        if missing_prerequisites:
            human_review = {"reason": "Missing prerequisites"}
        elif state.candidate_schedule is None:
            human_review = {"reason": "No valid schedule"}

        memory_snapshot = {
            "desired_subjects": state.extracted_preferences["desired_subjects"],
            "required_subjects": state.extracted_preferences.get("required_subjects", []),
            "avoid_days": state.extracted_preferences.get("avoid_days", []),
            "available_start": state.extracted_preferences.get("available_start"),
            "available_end": state.extracted_preferences.get("available_end"),
            "desired_province": state.extracted_preferences.get("desired_province"),
            "preferred_shift": state.extracted_preferences.get("preferred_shift"),
        }
        self.memory_store.save_state(
            session_id,
            student_id,
            {
                "memory_snapshot": memory_snapshot,
                "last_validation_report": state.validation_report,
            },
        )
        telemetry.event("agent.completed", escalated=bool(human_review))

        explanation = [
            f"Materias consideradas: {', '.join(state.extracted_preferences['desired_subjects'])}.",
            f"Provincia preferida: {state.extracted_preferences['desired_province']}.",
        ]
        return {
            "session_id": session_id,
            "assistant_message": (
                "Encontré un horario factible siguiendo el plan del agente."
                if state.candidate_schedule
                else "No encontré un horario válido con las restricciones actuales."
            ),
            "recommended_schedule": None
            if state.candidate_schedule is None
            else {key: value for key, value in state.candidate_schedule.items() if key != "_raw_result"},
            "tool_calls": state.tool_calls,
            "validation_report": state.validation_report,
            "human_review": human_review,
            "plan": self.planner.get_plan(),
            "memory_snapshot": memory_snapshot,
            "explanation": explanation,
            "warnings": [],
            "message_summary": json.dumps(
                {
                    "student_id": student_id,
                    "term": term,
                    "desired_subjects": state.extracted_preferences["desired_subjects"],
                },
                ensure_ascii=False,
            ),
        }
