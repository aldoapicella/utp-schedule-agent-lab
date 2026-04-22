from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from apps.api.main import app
from schedule_agent.monitoring.trace_viewer import iter_traces
from schedule_agent.orchestration.simple_agent import UTPPlanningAgent


def test_trace_file_is_written_after_agent_run() -> None:
    agent = UTPPlanningAgent()
    response = agent.respond(
        student_id="student_software_01",
        term="2026-1",
        message="Quiero Base de Datos II y Calidad de Software.",
        session_id="trace-session-1",
    )
    trace_file = Path("artifacts/traces") / f"{response['session_id']}.jsonl"
    assert trace_file.exists()
    events = iter_traces("artifacts/traces")
    assert any(event["event"] == "agent.started" for event in events)


def test_api_exposes_trace_and_agent_response() -> None:
    client = TestClient(app)
    response = client.post(
        "/api/v1/agent/respond",
        json={
            "student_id": "student_software_01",
            "term": "2026-1",
            "message": "Quiero Base de Datos II y Calidad de Software.",
        },
    )
    assert response.status_code == 200
    payload = response.json()
    trace_response = client.get(f"/api/v1/sessions/{payload['session_id']}/trace")
    assert trace_response.status_code == 200
    assert isinstance(trace_response.json(), list)
