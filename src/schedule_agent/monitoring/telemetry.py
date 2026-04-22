from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from schedule_agent.monitoring.structured_logger import StructuredLogger


class TelemetrySession:
    def __init__(self, trace_dir: str | Path, session_id: str) -> None:
        self.session_id = session_id
        self.logger = StructuredLogger(Path(trace_dir) / f"{session_id}.jsonl")

    def event(self, name: str, **payload: Any) -> None:
        self.logger.write(
            {
                "event": name,
                "session_id": self.session_id,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                **payload,
            }
        )

