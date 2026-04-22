from __future__ import annotations


class PlannerExecutor:
    STEPS = [
        "extract_preferences",
        "get_student_profile",
        "check_prerequisites",
        "get_available_groups",
        "calculate_best_schedule",
        "validate_schedule",
        "respond",
    ]

    def get_plan(self) -> list[str]:
        return list(self.STEPS)

