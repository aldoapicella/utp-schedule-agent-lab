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
