from __future__ import annotations

from schedule_agent.orchestration.simple_agent import UTPPlanningAgent


def test_agent_returns_structured_schedule_and_tool_calls() -> None:
    agent = UTPPlanningAgent()
    response = agent.respond(
        student_id="student_software_01",
        term="2026-1",
        message="Quiero Base de Datos II y Calidad de Software. No puedo viernes y solo puedo despues de las 5 p.m.",
    )

    assert response["recommended_schedule"] is not None
    assert response["human_review"] is None
    assert response["tool_calls"]
    assert response["validation_report"]["hard_constraints"]["prerequisites_satisfied"] is True


def test_agent_escalates_when_prerequisites_are_missing() -> None:
    agent = UTPPlanningAgent()
    response = agent.respond(
        student_id="student_software_02",
        term="2026-1",
        message="Quiero Base de Datos II y Arquitectura de Software, esta ultima es obligatoria.",
    )

    assert response["human_review"] is not None
    assert response["human_review"]["reason"] == "Missing prerequisites"

