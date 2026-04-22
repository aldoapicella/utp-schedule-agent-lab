from __future__ import annotations

from schedule_agent.orchestration.simple_agent import UTPPlanningAgent


def test_agent_returns_plan_and_structured_schedule() -> None:
    agent = UTPPlanningAgent()
    response = agent.respond(
        student_id="student_software_01",
        term="2026-1",
        message="Quiero Base de Datos II y Calidad de Software. No puedo viernes y solo puedo despues de las 5 p.m.",
    )

    assert response["recommended_schedule"] is not None
    assert response["plan"] == [
        "extract_preferences",
        "get_student_profile",
        "check_prerequisites",
        "get_available_groups",
        "calculate_best_schedule",
        "validate_schedule",
        "respond",
    ]


def test_agent_tool_order_follows_the_plan() -> None:
    agent = UTPPlanningAgent()
    response = agent.respond(
        student_id="student_software_01",
        term="2026-1",
        message="Quiero Base de Datos II y Calidad de Software.",
    )
    tool_names = [call["name"] for call in response["tool_calls"]]
    assert tool_names == [
        "get_student_profile",
        "check_prerequisites",
        "get_available_groups",
        "calculate_best_schedule",
        "validate_schedule",
    ]
