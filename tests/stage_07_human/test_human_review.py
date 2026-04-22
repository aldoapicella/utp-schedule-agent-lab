from __future__ import annotations

from schedule_agent.human.advisor_console import AdvisorConsole
from schedule_agent.human.approval_queue import ApprovalQueue


def test_approval_queue_and_console_round_trip(tmp_path) -> None:
    queue = ApprovalQueue(tmp_path / "lab.db")
    queue.create("Missing prerequisites", {"student_id": "student_software_02"})

    console = AdvisorConsole(queue)
    tickets = console.summarize_open_tickets()

    assert tickets
    assert tickets[0]["reason"] == "Missing prerequisites"

