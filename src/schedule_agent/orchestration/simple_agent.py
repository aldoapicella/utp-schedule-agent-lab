from __future__ import annotations

import os
import time
import uuid
from datetime import datetime
from dataclasses import asdict, is_dataclass
from pathlib import Path
from typing import Any

from schedule_calculator.adapters.in_memory_repository import InMemoryGroupCatalogRepository
from schedule_calculator.application.scheduler import SchedulerService
from schedule_calculator.domain.rules import all_sessions_virtual, schedule_within_available
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
from schedule_agent.tools.schedule_tools import ScheduleTools, _FilteredRepository


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


DAY_LABELS = {
    "MONDAY": "lunes",
    "TUESDAY": "martes",
    "WEDNESDAY": "miercoles",
    "THURSDAY": "jueves",
    "FRIDAY": "viernes",
    "SATURDAY": "sabado",
    "SUNDAY": "domingo",
}


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

    @staticmethod
    def _parse_clock(value: str):
        return datetime.strptime(value, "%H:%M").time()

    @staticmethod
    def _format_day_list(days: list[str] | set[str]) -> str:
        labels = [DAY_LABELS.get(day, day.lower()) for day in sorted(set(days))]
        if not labels:
            return ""
        if len(labels) == 1:
            return labels[0]
        return ", ".join(labels[:-1]) + f" y {labels[-1]}"

    def _subject_name(self, subject_id: str) -> str:
        subject = self.catalog.get_subject(subject_id)
        return subject.name if subject else subject_id

    def _build_schedule_payload(
        self,
        *,
        subject_ids: list[str],
        preferences: dict[str, Any],
    ) -> dict[str, Any]:
        return {
            "desired_subjects": subject_ids,
            "required_subjects": preferences.get("required_subjects", []),
            "available_start": preferences.get("available_start", "08:00"),
            "available_end": preferences.get("available_end", "22:30"),
            "desired_province": preferences["desired_province"],
            "avoid_days": preferences.get("avoid_days", []),
        }

    def _groups_matching_preferences(self, subject_id: str, province: str, repository=None) -> list[Any]:
        source = repository or self.group_repository
        return [
            group
            for group in source.list_groups_for_subject(subject_id)
            if group.province.upper() == province.upper() or all_sessions_virtual(group.sessions)
        ]

    def _group_is_feasible_within_time(self, group: Any, preferences: dict[str, Any]) -> bool:
        return schedule_within_available(
            group.sessions,
            self._parse_clock(preferences.get("available_start", "08:00")),
            self._parse_clock(preferences.get("available_end", "22:30")),
        )

    def _build_no_schedule_suggestions(
        self,
        *,
        student_profile: dict[str, Any],
        subject_ids: list[str],
        preferences: dict[str, Any],
        missing_prereqs: dict[str, list[str]],
    ) -> list[str]:
        suggestions: list[str] = []

        def append_unique(message: str) -> None:
            if message and message not in suggestions:
                suggestions.append(message)

        province = preferences["desired_province"]
        avoid_days = set(preferences.get("avoid_days", []))
        payload = self._build_schedule_payload(subject_ids=subject_ids, preferences=preferences)

        if avoid_days:
            for day in sorted(avoid_days):
                relaxed_payload = dict(payload)
                relaxed_payload["avoid_days"] = [
                    blocked_day for blocked_day in payload.get("avoid_days", []) if blocked_day != day
                ]
                relaxed_schedule = self.schedule_tools.calculate_best_schedule(relaxed_payload)
                if relaxed_schedule:
                    chosen_names = ", ".join(
                        item["subject_name"] for item in relaxed_schedule["chosen_enrollments"]
                    )
                    append_unique(
                        f"Si flexibilizas {self._format_day_list([day])}, aparece una alternativa para {chosen_names}."
                    )
                    break

            filtered_repository = _FilteredRepository(self.scheduler.repository, avoid_days)
            for subject_id in subject_ids:
                relaxed_groups = self._groups_matching_preferences(subject_id, province)
                strict_groups = self._groups_matching_preferences(
                    subject_id,
                    province,
                    repository=filtered_repository,
                )
                if relaxed_groups and not strict_groups:
                    blocked_days = {
                        session.day.upper()
                        for group in relaxed_groups
                        for session in group.sessions
                        if session.day.upper() in avoid_days and not all_sessions_virtual(group.sessions)
                    }
                    append_unique(
                        f"{self._subject_name(subject_id)} solo tiene grupos compatibles en "
                        f"{self._format_day_list(blocked_days)} con tus filtros actuales."
                    )

        if payload["available_start"] != "08:00":
            relaxed_payload = dict(payload)
            relaxed_payload["available_start"] = "08:00"
            relaxed_schedule = self.schedule_tools.calculate_best_schedule(relaxed_payload)
            if relaxed_schedule:
                chosen_names = ", ".join(
                    item["subject_name"] for item in relaxed_schedule["chosen_enrollments"]
                )
                append_unique(
                    f"Si amplias tu disponibilidad antes de las {payload['available_start']}, "
                    f"aparece una alternativa para {chosen_names}."
                )

        best_subset: tuple[str, dict[str, Any]] | None = None
        for removed_subject in subject_ids:
            remaining_subjects = [subject_id for subject_id in subject_ids if subject_id != removed_subject]
            if len(remaining_subjects) < 2:
                continue
            subset_payload = self._build_schedule_payload(
                subject_ids=remaining_subjects,
                preferences=preferences,
            )
            subset_schedule = self.schedule_tools.calculate_best_schedule(subset_payload)
            if subset_schedule is None:
                continue
            if best_subset is None:
                best_subset = (removed_subject, subset_schedule)
                continue
            current_count = len(subset_schedule["chosen_enrollments"])
            best_count = len(best_subset[1]["chosen_enrollments"])
            current_idle = int(subset_schedule["total_idle_minutes"])
            best_idle = int(best_subset[1]["total_idle_minutes"])
            if current_count > best_count or (current_count == best_count and current_idle < best_idle):
                best_subset = (removed_subject, subset_schedule)

        approved_subjects = set(student_profile.get("approved_subjects", []))
        for subject_id in subject_ids:
            if subject_id in approved_subjects:
                append_unique(
                    f"Ya tienes aprobada {self._subject_name(subject_id)}. "
                    "Quitarla de la solicitud puede destrabar una combinacion mas realista."
                )

        if best_subset is not None:
            removed_subject, subset_schedule = best_subset
            chosen_names = ", ".join(
                item["subject_name"] for item in subset_schedule["chosen_enrollments"]
            )
            append_unique(
                f"Con las restricciones actuales si puedo armar {chosen_names}. "
                f"Prueba quitando {self._subject_name(removed_subject)}."
            )

        individually_feasible: list[str] = []
        filtered_repository = _FilteredRepository(self.scheduler.repository, avoid_days)
        for subject_id in subject_ids:
            strict_groups = self._groups_matching_preferences(
                subject_id,
                province,
                repository=filtered_repository,
            )
            if any(self._group_is_feasible_within_time(group, preferences) for group in strict_groups):
                individually_feasible.append(self._subject_name(subject_id))
        if individually_feasible and best_subset is None:
            append_unique(
                "Con tus filtros actuales solo veo opciones aisladas para "
                + ", ".join(individually_feasible)
                + ". Para combinar mas materias tendras que flexibilizar dia u horario."
            )

        if missing_prereqs:
            for subject_id, prereqs in missing_prereqs.items():
                prereq_names = ", ".join(self._subject_name(prereq_id) for prereq_id in prereqs)
                append_unique(
                    f"Primero necesitas aprobar {prereq_names} antes de pedir {self._subject_name(subject_id)}."
                )

        if not suggestions:
            append_unique(
                "Prueba quitando una materia, ampliando horario o flexibilizando uno de los dias bloqueados."
            )

        return suggestions[:4]

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
        if not subject_ids and not guard_result.escalate:
            warning = (
                "No pude identificar materias concretas en tu mensaje. "
                "Usa nombres del catálogo como Base de Datos II, Calidad de Software, "
                "Arquitectura de Software o Redes I."
            )
            state.warnings.append(warning)
            memory_snapshot = {
                "desired_subjects": [],
                "required_subjects": state.extracted_preferences.get("required_subjects", []),
                "avoid_days": state.extracted_preferences.get("avoid_days", []),
                "available_start": state.extracted_preferences.get("available_start"),
                "available_end": state.extracted_preferences.get("available_end"),
                "desired_province": state.extracted_preferences.get("desired_province"),
                "preferred_shift": state.extracted_preferences.get("preferred_shift"),
                "max_credits": state.extracted_preferences.get("max_credits"),
            }
            validation_report = {
                "hard_constraints": {"has_schedule": False},
                "warnings": [warning],
                "metrics": {"subject_count": 0, "requested_subjects": 0},
            }
            self.memory_store.save_state(
                session_id,
                student_id,
                {
                    "memory_snapshot": memory_snapshot,
                    "student_profile": state.student_profile,
                    "last_validation_report": validation_report,
                    "last_human_review": None,
                },
            )
            telemetry.event("agent.completed", escalated=False, reason="subjects_not_identified")
            return {
                "session_id": session_id,
                "assistant_message": "No pude identificar las materias de tu solicitud.",
                "recommended_schedule": None,
                "explanation": [
                    warning,
                    "Ajusta la solicitud y vuelve a intentar con nombres del catálogo sintético.",
                ],
                "tool_calls": state.tool_calls,
                "memory_snapshot": memory_snapshot,
                "validation_report": validation_report,
                "human_review": None,
                "warnings": state.warnings,
                "plan": self.planner.get_plan(),
            }

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

        selected_subject_count = (
            len(state.candidate_schedule["chosen_enrollments"]) if state.candidate_schedule else 0
        )
        needs_recovery_guidance = selected_subject_count < len(subject_ids)
        recovery_suggestions: list[str] = []
        if needs_recovery_guidance:
            recovery_suggestions = self._build_no_schedule_suggestions(
                student_profile=state.student_profile,
                subject_ids=subject_ids,
                preferences=state.extracted_preferences,
                missing_prereqs=missing_prereqs,
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
        if state.extracted_preferences.get("avoid_days"):
            explanation_lines.append(
                "Dias bloqueados: "
                f"{self._format_day_list(state.extracted_preferences.get('avoid_days', []))}."
            )
        if state.validation_report["warnings"]:
            explanation_lines.extend(state.validation_report["warnings"])
        if needs_recovery_guidance:
            if state.candidate_schedule is None:
                explanation_lines.append(
                    "No encontre una combinacion que cumpla todas las restricciones al mismo tiempo."
                )
            else:
                explanation_lines.append(
                    f"Solo pude incluir {selected_subject_count} de {len(subject_ids)} materias solicitadas."
                )
            explanation_lines.extend(recovery_suggestions)
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
                "requested_subject_count": len(subject_ids),
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
