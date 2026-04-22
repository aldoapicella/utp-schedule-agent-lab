from __future__ import annotations

from fastapi.testclient import TestClient

from apps.api.main import app
from schedule_agent.human.advisor_console import AdvisorConsole
from schedule_agent.human.approval_queue import ApprovalQueue
from schedule_agent.orchestration.simple_agent import UTPPlanningAgent


def test_approval_queue_and_console_round_trip(tmp_path) -> None:
    queue = ApprovalQueue(tmp_path / "lab.db")
    queue.create("Missing prerequisites", {"student_id": "student_software_02"})

    console = AdvisorConsole(queue)
    tickets = console.summarize_open_tickets()

    assert tickets
    assert tickets[0]["reason"] == "Missing prerequisites"


def test_agent_creates_human_review_ticket_for_missing_prerequisites() -> None:
    agent = UTPPlanningAgent()
    response = agent.respond(
        student_id="student_software_02",
        term="2026-1",
        message="Quiero Arquitectura de Software y Base de Datos II.",
    )

    assert response["human_review"] is not None
    assert response["human_review"]["status"] == "queued"
    assert response["human_review"]["assigned_role"] == "academic_advisor"


def test_api_creates_human_review_ticket() -> None:
    client = TestClient(app)
    response = client.post(
        "/api/v1/human-review",
        json={
            "reason": "Missing prerequisites",
            "payload": {"student_id": "student_software_02"},
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "queued"
    assert payload["assigned_role"] == "academic_advisor"
