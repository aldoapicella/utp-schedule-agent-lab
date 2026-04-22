from __future__ import annotations

from schedule_calculator.domain.models import CandidateEnrollment, ScheduleResult


def format_schedule_summary(result: ScheduleResult | None) -> str:
    if result is None:
        return "No valid schedule found."
    lines = [
        "Recommended schedule:",
        *[
            f"- {format_enrollment_label(enrollment, include_subject_name=True)}"
            for enrollment in result.chosen_enrollments
        ],
        f"Total idle time: {result.total_idle_minutes} minutes",
    ]
    return "\n".join(lines)


def format_enrollment_label(
    enrollment: CandidateEnrollment,
    *,
    include_subject_name: bool = False,
) -> str:
    lab_codes = {
        session.lab_code
        for session in enrollment.sessions
        if session.session_type.lower() == "laboratory" and session.lab_code
    }
    subject_label = enrollment.subject_id
    if include_subject_name and enrollment.subject_name:
        subject_label = f"{enrollment.subject_id} {enrollment.subject_name}"
    details: list[str] = []
    if enrollment.hour_code:
        details.append(f"CODHORA: {enrollment.hour_code}")
    if lab_codes:
        details.append(f"Lab: {', '.join(sorted(lab_codes))}")
    if details:
        return f"{subject_label}:{enrollment.group_code} ({', '.join(details)})"
    return f"{subject_label}:{enrollment.group_code}"

