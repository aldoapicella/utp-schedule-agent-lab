from __future__ import annotations

from schedule_agent.orchestration.simple_agent import UTPPlanningAgent


def test_session_memory_reuses_previous_preferences() -> None:
    agent = UTPPlanningAgent()
    first = agent.respond(
        student_id="student_software_01",
        term="2026-1",
        message="Recuerda que trabajo hasta las 5 y no puedo viernes.",
        session_id="memory-session-1",
    )
    second = agent.respond(
        student_id="student_software_01",
        term="2026-1",
        message="Ahora recomiendame un horario con Base de Datos II y Calidad de Software.",
        session_id="memory-session-1",
    )

    assert "FRIDAY" in first["memory_snapshot"]["avoid_days"]
    assert second["memory_snapshot"]["available_start"] == "17:00"
    assert "FRIDAY" in second["memory_snapshot"]["avoid_days"]


def test_session_memory_does_not_pin_previous_subjects_when_prompt_changes() -> None:
    agent = UTPPlanningAgent()
    agent.respond(
        student_id="student_software_01",
        term="2026-1",
        message="Quiero tomar Base de Datos II y Calidad de Software.",
        session_id="memory-session-2",
    )
    second = agent.respond(
        student_id="student_software_01",
        term="2026-1",
        message="Quiero tomar Arquitectura de Software y Redes 1.",
        session_id="memory-session-2",
    )

    assert set(second["memory_snapshot"]["desired_subjects"]) == {"0760", "0755"}


def test_short_natural_preference_phrases_are_extracted() -> None:
    agent = UTPPlanningAgent()

    response = agent.respond(
        student_id="student_software_01",
        term="2026-1",
        message="Quiero tomar BD II y calidad. Prefiero noche y no viernes.",
    )

    assert response["memory_snapshot"]["available_start"] == "17:00"
    assert response["memory_snapshot"]["preferred_shift"] == "EVENING"
    assert "FRIDAY" in response["memory_snapshot"]["avoid_days"]
    assert set(response["memory_snapshot"]["desired_subjects"]) == {"5003", "0692"}
