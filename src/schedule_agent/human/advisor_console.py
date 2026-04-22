from __future__ import annotations

from schedule_agent.human.approval_queue import ApprovalQueue


class AdvisorConsole:
    def __init__(self, queue: ApprovalQueue) -> None:
        self.queue = queue

    def summarize_open_tickets(self) -> list[dict]:
        return [ticket.to_dict() for ticket in self.queue.list_open()]

