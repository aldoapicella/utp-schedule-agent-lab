from __future__ import annotations

from datetime import datetime

from schedule_calculator.domain.models import ScheduleResult
from schedule_agent.data.catalog import CatalogStore
from schedule_agent.tools.schemas import ValidationReport

DAY_LABELS = {
    "MONDAY": "lunes",
    "TUESDAY": "martes",
    "WEDNESDAY": "miercoles",
    "THURSDAY": "jueves",
    "FRIDAY": "viernes",
    "SATURDAY": "sabado",
    "SUNDAY": "domingo",
}


def _parse_time(value: str):
    return datetime.strptime(value, "%H:%M").time()


def _format_day_list(days: set[str]) -> str:
    labels = [DAY_LABELS.get(day, day.lower()) for day in sorted(days)]
    if not labels:
        return ""
    if len(labels) == 1:
        return labels[0]
    return ", ".join(labels[:-1]) + f" y {labels[-1]}"


def validate_schedule_constraints(
    *,
    result: ScheduleResult | None,
    preferences: dict,
    catalog: CatalogStore,
    missing_prerequisites: dict[str, list[str]],
) -> ValidationReport:
    max_credits = preferences.get("max_credits")
    if result is None:
        return ValidationReport(
            hard_constraints={
                "has_schedule": False,
                "no_conflicts": False,
                "within_availability": False,
                "province_or_virtual": False,
                "prerequisites_satisfied": not missing_prerequisites,
                "within_max_credits": True,
            },
            warnings=["No encontre un horario que cumpla todas las restricciones actuales."],
            metrics={},
        )

    avoid_days = set(preferences.get("avoid_days", []))
    no_avoid_day_violation = not any(
        session.day.upper() in avoid_days for session in result.final_schedule
    )
    total_credits = catalog.total_credits(
        [enrollment.subject_id for enrollment in result.chosen_enrollments]
    )
    within_max_credits = max_credits is None or total_credits <= max_credits
    warnings: list[str] = []
    if not no_avoid_day_violation:
        warnings.append(
            f"El horario seleccionado incluye clases en {_format_day_list(avoid_days)}, "
            "que estan bloqueados por la disponibilidad del estudiante."
        )
    if not within_max_credits:
        warnings.append("El horario seleccionado excede el maximo de creditos del estudiante.")
    return ValidationReport(
        hard_constraints={
            "has_schedule": True,
            "no_conflicts": True,
            "within_availability": True,
            "province_or_virtual": True,
            "prerequisites_satisfied": not missing_prerequisites,
            "avoid_days_respected": no_avoid_day_violation,
            "within_max_credits": within_max_credits,
        },
        warnings=warnings,
        metrics={
            "subject_count": len(result.chosen_enrollments),
            "total_idle_minutes": result.total_idle_minutes,
            "total_credits": total_credits,
            "requested_subjects": len(preferences.get("desired_subjects", [])),
        },
    )
