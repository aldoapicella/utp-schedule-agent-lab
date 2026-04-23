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


def test_agent_respects_no_thursday_and_explains_partial_schedule() -> None:
    agent = UTPPlanningAgent()

    response = agent.respond(
        student_id="student_software_01",
        term="2026-1",
        message=(
            "Quiero tomar Base de Datos II, Calidad de Software y Org. y Arq. de Computadora. "
            "Solo puedo despues de las 5 p.m. y no puedo jueves."
        ),
    )

    assert "THURSDAY" in response["memory_snapshot"]["avoid_days"]
    assert response["recommended_schedule"] is not None
    assert all(item["day"] != "THURSDAY" for item in response["recommended_schedule"]["schedule"])
    assert {
        item["subject_id"] for item in response["recommended_schedule"]["chosen_enrollments"]
    } == {"5003", "0692"}
    assert any("Solo pude incluir 2 de 3 materias" in line for line in response["explanation"])
    assert any("flexibilizas jueves" in line.lower() for line in response["explanation"])
