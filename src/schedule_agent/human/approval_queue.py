from __future__ import annotations

import json
import sqlite3
import uuid
from pathlib import Path

from schedule_agent.tools.schemas import HumanReviewTicket


class ApprovalQueue:
    def __init__(self, database_path: str | Path) -> None:
        self.database_path = Path(database_path)
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        self._ensure_tables()

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.database_path)

    def _ensure_tables(self) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS human_review_queue (
                    ticket_id TEXT PRIMARY KEY,
                    status TEXT NOT NULL,
                    reason TEXT NOT NULL,
                    assigned_role TEXT NOT NULL,
                    payload_json TEXT NOT NULL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            connection.commit()

    def create(self, reason: str, payload: dict) -> HumanReviewTicket:
        ticket = HumanReviewTicket(
            ticket_id=str(uuid.uuid4()),
            status="queued",
            reason=reason,
            assigned_role="academic_advisor",
            payload=payload,
        )
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO human_review_queue (ticket_id, status, reason, assigned_role, payload_json)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    ticket.ticket_id,
                    ticket.status,
                    ticket.reason,
                    ticket.assigned_role,
                    json.dumps(payload, ensure_ascii=False),
                ),
            )
            connection.commit()
        return ticket

    def list_open(self) -> list[HumanReviewTicket]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT ticket_id, status, reason, assigned_role, payload_json
                FROM human_review_queue
                ORDER BY created_at DESC
                """
            ).fetchall()
        return [
            HumanReviewTicket(
                ticket_id=row[0],
                status=row[1],
                reason=row[2],
                assigned_role=row[3],
                payload=json.loads(row[4]),
            )
            for row in rows
        ]

