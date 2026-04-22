from __future__ import annotations

import json
import os
import uuid
from pathlib import Path

from schedule_calculator.adapters.in_memory_repository import InMemoryGroupCatalogRepository
from schedule_calculator.application.scheduler import SchedulerService
from schedule_agent.data.catalog import CatalogStore, default_data_dir
from schedule_agent.memory.preference_extractor import PreferenceExtractor
from schedule_agent.memory.session_memory import SessionMemoryStore
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
        self.catalog = CatalogStore(self.data_dir)
        self.group_repository = InMemoryGroupCatalogRepository.from_json(self.data_dir / "group_catalog.json")
        self.scheduler = SchedulerService(self.group_repository)
        self.catalog_tools = CatalogTools(self.catalog, self.group_repository)
        self.schedule_tools = ScheduleTools(self.catalog, self.scheduler)
        self.planner = PlannerExecutor()
        self.preference_extractor = PreferenceExtractor(self.catalog)
        self.memory_store = SessionMemoryStore(self.database_path)

    def _record(self, name: str, input_summary: dict, output_summary: dict) -> dict:
        return ToolCallRecord(
            name=name,
            status="succeeded",
            input_summary=input_summary,
            output_summary=output_summary,
        ).to_dict()

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
        previous_state = self.memory_store.load_state(session_id) or {}
        state = AgentState(student_id=student_id, user_message=message)
        state.student_profile = self.catalog_tools.get_student_profile(student_id)
        state.tool_calls.append(
            self._record("get_student_profile", {"student_id": student_id}, state.student_profile or {})
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

        if not state.extracted_preferences["desired_subjects"]:
            available = self.catalog_tools.list_available_subjects(career or state.student_profile["career"], term)
            state.extracted_preferences["desired_subjects"] = [subject["subject_id"] for subject in available[:3]]
            state.tool_calls.append(
                self._record(
                    "list_available_subjects",
                    {"career_code": career or state.student_profile["career"], "term": term},
                    {"count": len(available)},
                )
            )

        missing_prerequisites = self.catalog_tools.check_prerequisites(
            student_id,
            state.extracted_preferences["desired_subjects"],
        )
        state.tool_calls.append(
            self._record(
                "check_prerequisites",
                {
                    "student_id": student_id,
                    "subject_ids": state.extracted_preferences["desired_subjects"],
                },
                missing_prerequisites,
            )
        )

        available_groups = self.catalog_tools.get_available_groups(
            state.extracted_preferences["desired_subjects"],
            state.extracted_preferences["desired_province"],
        )
        state.tool_calls.append(
            self._record(
                "get_available_groups",
                {
                    "subject_ids": state.extracted_preferences["desired_subjects"],
                    "province": state.extracted_preferences["desired_province"],
                },
                {key: len(value) for key, value in available_groups.items()},
            )
        )

        state.candidate_schedule = self.schedule_tools.calculate_best_schedule(state.extracted_preferences)
        state.tool_calls.append(
            self._record(
                "calculate_best_schedule",
                {"payload": state.extracted_preferences},
                {"has_schedule": state.candidate_schedule is not None},
            )
        )

        state.validation_report = self.schedule_tools.validate_schedule(
            schedule_payload=state.candidate_schedule,
            preferences=state.extracted_preferences,
            missing_prerequisites=missing_prerequisites,
        )
        state.tool_calls.append(
            self._record(
                "validate_schedule",
                {"missing_prerequisites": missing_prerequisites},
                state.validation_report,
            )
        )

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
            "human_review": None,
            "plan": self.planner.get_plan(),
            "memory_snapshot": memory_snapshot,
            "message_summary": json.dumps(
                {
                    "student_id": student_id,
                    "term": term,
                    "desired_subjects": state.extracted_preferences["desired_subjects"],
                },
                ensure_ascii=False,
            ),
        }
