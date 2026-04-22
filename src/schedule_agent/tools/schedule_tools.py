from __future__ import annotations

from datetime import datetime

from schedule_calculator.application.scheduler import SchedulerService
from schedule_calculator.domain.models import CourseGroup, ScheduleRequest
from schedule_calculator.domain.rules import all_sessions_virtual
from schedule_agent.data.catalog import CatalogStore
from schedule_agent.tools.schemas import ValidationReport


def _parse_time(value: str):
    return datetime.strptime(value, "%H:%M").time()


class _FilteredRepository:
    def __init__(self, source_repository, avoid_days: set[str]) -> None:
        self.source_repository = source_repository
        self.avoid_days = avoid_days

    def list_groups_for_subject(self, subject_id: str) -> list[CourseGroup]:
        groups = self.source_repository.list_groups_for_subject(subject_id)
        if not self.avoid_days:
            return groups
        filtered: list[CourseGroup] = []
        for group in groups:
            if any(session.day.upper() in self.avoid_days for session in group.sessions):
                if not all_sessions_virtual(group.sessions):
                    continue
            filtered.append(group)
        return filtered


class ScheduleTools:
    def __init__(self, catalog: CatalogStore, scheduler: SchedulerService) -> None:
        self.catalog = catalog
        self.scheduler = scheduler

    def calculate_best_schedule(self, payload: dict) -> dict | None:
        avoid_days = {day.upper() for day in payload.get("avoid_days", [])}
        scheduler = self.scheduler
        if avoid_days:
            scheduler = SchedulerService(_FilteredRepository(self.scheduler.repository, avoid_days))
        request = ScheduleRequest(
            desired_subjects=payload["desired_subjects"],
            required_subjects=payload.get("required_subjects", []),
            available_start=_parse_time(payload.get("available_start", "08:00")),
            available_end=_parse_time(payload.get("available_end", "22:30")),
            desired_province=payload["desired_province"],
        )
        result = scheduler.find_best_schedule(request)
        if result is None:
            return None

        subject_names = {
            enrollment.subject_id: enrollment.subject_name or enrollment.subject_id
            for enrollment in result.chosen_enrollments
        }
        return {
            "chosen_enrollments": [
                {
                    "subject_id": enrollment.subject_id,
                    "subject_name": enrollment.subject_name,
                    "group_code": enrollment.group_code,
                    "hour_code": enrollment.hour_code,
                }
                for enrollment in result.chosen_enrollments
            ],
            "total_idle_minutes": result.total_idle_minutes,
            "schedule": [
                {
                    "day": session.day,
                    "subject_id": session.subject,
                    "subject_name": subject_names.get(session.subject, session.subject),
                    "session_type": session.session_type,
                    "classroom": session.classroom,
                    "start_time": session.start_time.strftime("%H:%M") if session.start_time else "",
                    "end_time": session.end_time.strftime("%H:%M") if session.end_time else "",
                    "lab_code": session.lab_code,
                }
                for session in result.final_schedule
            ],
            "_raw_result": result,
        }

    def validate_schedule(
        self,
        *,
        schedule_payload: dict | None,
        preferences: dict,
        missing_prerequisites: dict[str, list[str]],
    ) -> dict:
        if schedule_payload is None:
            return ValidationReport(
                hard_constraints={
                    "has_schedule": False,
                    "no_conflicts": False,
                    "within_availability": False,
                    "province_or_virtual": False,
                    "prerequisites_satisfied": not bool(missing_prerequisites),
                },
                warnings=["No valid schedule found with the current inputs."],
                metrics={},
            ).to_dict()

        raw_result = schedule_payload["_raw_result"]
        available_start = _parse_time(preferences.get("available_start", "08:00"))
        available_end = _parse_time(preferences.get("available_end", "22:30"))
        avoid_days = {day.upper() for day in preferences.get("avoid_days", [])}

        within_availability = all(
            session.start_time >= available_start and session.end_time <= available_end
            for enrollment in raw_result.chosen_enrollments
            for session in enrollment.sessions
        )
        province_or_virtual = all(
            enrollment.province.upper() == preferences["desired_province"].upper()
            or all_sessions_virtual(enrollment.sessions)
            for enrollment in raw_result.chosen_enrollments
        )
        avoid_days_respected = all(
            session.day.upper() not in avoid_days or session.classroom.upper() == "VVIRT"
            for enrollment in raw_result.chosen_enrollments
            for session in enrollment.sessions
        )
        report = ValidationReport(
            hard_constraints={
                "has_schedule": True,
                "no_conflicts": True,
                "within_availability": within_availability,
                "province_or_virtual": province_or_virtual,
                "prerequisites_satisfied": not bool(missing_prerequisites),
                "avoid_days_respected": avoid_days_respected,
            },
            warnings=[],
            metrics={
                "subject_count": len(raw_result.chosen_enrollments),
                "total_idle_minutes": raw_result.total_idle_minutes,
                "total_credits": self.catalog.total_credits(
                    [enrollment.subject_id for enrollment in raw_result.chosen_enrollments]
                ),
            },
        )
        return report.to_dict()
