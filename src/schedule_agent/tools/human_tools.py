from __future__ import annotations

from schedule_agent.human.approval_queue import ApprovalQueue


class HumanTools:
    def __init__(self, queue: ApprovalQueue) -> None:
        self.queue = queue

    def request_human_review(self, reason: str, payload: dict) -> dict:
        return self.queue.create(reason, payload).to_dict()

