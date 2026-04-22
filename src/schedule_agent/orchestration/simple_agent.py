from __future__ import annotations

import json
from pathlib import Path

from schedule_calculator.adapters.in_memory_repository import InMemoryGroupCatalogRepository
from schedule_calculator.application.scheduler import SchedulerService
from schedule_agent.data.catalog import CatalogStore, default_data_dir, normalize_text
from schedule_agent.orchestration.planner_executor import PlannerExecutor
from schedule_agent.orchestration.state import AgentState
from schedule_agent.tools.catalog_tools import CatalogTools
from schedule_agent.tools.schedule_tools import ScheduleTools
from schedule_agent.tools.schemas import ToolCallRecord


class UTPPlanningAgent:
    def __init__(self, data_dir: str | Path | None = None) -> None:
        self.data_dir = Path(data_dir or default_data_dir())
        self.catalog = CatalogStore(self.data_dir)
        self.group_repository = InMemoryGroupCatalogRepository.from_json(self.data_dir / "group_catalog.json")
        self.scheduler = SchedulerService(self.group_repository)
        self.catalog_tools = CatalogTools(self.catalog, self.group_repository)
        self.schedule_tools = ScheduleTools(self.catalog, self.scheduler)
        self.planner = PlannerExecutor()

    def _record(self, name: str, input_summary: dict, output_summary: dict) -> dict:
        return ToolCallRecord(
            name=name,
            status="succeeded",
            input_summary=input_summary,
            output_summary=output_summary,
        ).to_dict()

    def _extract_preferences(self, message: str, default_province: str) -> dict:
        normalized_message = normalize_text(message)
        return {
            "desired_subjects": self.catalog.resolve_subject_ids_from_text(message),
            "desired_province": default_province,
            "avoid_days": ["FRIDAY"] if "VIERNES" in normalized_message else [],
            "available_start": "17:00" if "5 P.M" in normalized_message or "DESPUES DE LAS 5" in normalized_message else "08:00",
            "available_end": "22:30",
            "required_subjects": [],
        }

    def respond(
        self,
        *,
        student_id: str,
        message: str,
        term: str,
        career: str | None = None,
    ) -> dict:
        state = AgentState(student_id=student_id, user_message=message)
        state.student_profile = self.catalog_tools.get_student_profile(student_id)
        state.tool_calls.append(
            self._record("get_student_profile", {"student_id": student_id}, state.student_profile or {})
        )
        if state.student_profile is None:
            raise ValueError(f"Unknown student_id '{student_id}'.")

        state.extracted_preferences = self._extract_preferences(message, state.student_profile["current_province"])
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

        return {
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
            "message_summary": json.dumps(
                {
                    "student_id": student_id,
                    "term": term,
                    "desired_subjects": state.extracted_preferences["desired_subjects"],
                },
                ensure_ascii=False,
            ),
        }
