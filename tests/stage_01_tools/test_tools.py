from __future__ import annotations

from schedule_agent.orchestration.simple_agent import UTPPlanningAgent


def test_check_prerequisites_returns_missing_subjects() -> None:
    agent = UTPPlanningAgent()
    missing = agent.catalog_tools.check_prerequisites(
        "student_software_02",
        ["5003", "0760"],
    )
    assert missing == {"0760": ["0692"]}


def test_calculate_best_schedule_respects_no_friday_preference() -> None:
    agent = UTPPlanningAgent()
    payload = {
        "desired_subjects": ["5003", "0692"],
        "required_subjects": [],
        "available_start": "17:00",
        "available_end": "22:30",
        "desired_province": "PANAMÁ",
        "avoid_days": ["FRIDAY"],
    }
    result = agent.schedule_tools.calculate_best_schedule(payload)
    assert result is not None
    assert all(item["day"] != "FRIDAY" for item in result["schedule"])


def test_calculate_best_schedule_includes_subject_metadata_for_timetable() -> None:
    agent = UTPPlanningAgent()
    payload = {
        "desired_subjects": ["5003", "0692"],
        "required_subjects": [],
        "available_start": "17:00",
        "available_end": "22:30",
        "desired_province": "PANAMÁ",
        "avoid_days": [],
    }
    result = agent.schedule_tools.calculate_best_schedule(payload)
    assert result is not None
    assert all(item["subject_id"] for item in result["schedule"])
    assert all(item["subject_name"] for item in result["schedule"])
