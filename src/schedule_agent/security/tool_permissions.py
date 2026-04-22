from __future__ import annotations


ALLOWED_TOOLS = {
    "get_student_profile",
    "list_available_subjects",
    "get_available_groups",
    "check_prerequisites",
    "calculate_best_schedule",
    "validate_schedule",
    "request_human_review",
}


def assert_tool_allowed(tool_name: str) -> None:
    if tool_name not in ALLOWED_TOOLS:
        raise PermissionError(f"Tool '{tool_name}' is not allowed.")
