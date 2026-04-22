from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any


class SessionMemoryStore:
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
                CREATE TABLE IF NOT EXISTS sessions (
                    session_id TEXT PRIMARY KEY,
                    student_id TEXT NOT NULL,
                    state_json TEXT NOT NULL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            connection.commit()

    def load_state(self, session_id: str) -> dict[str, Any] | None:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT state_json FROM sessions WHERE session_id = ?",
                (session_id,),
            ).fetchone()
        if not row:
            return None
        return json.loads(row[0])

    def save_state(self, session_id: str, student_id: str, state: dict[str, Any]) -> None:
        payload = json.dumps(state, ensure_ascii=False)
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO sessions (session_id, student_id, state_json, updated_at)
                VALUES (?, ?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(session_id) DO UPDATE SET
                    student_id = excluded.student_id,
                    state_json = excluded.state_json,
                    updated_at = CURRENT_TIMESTAMP
                """,
                (session_id, student_id, payload),
            )
            connection.commit()

