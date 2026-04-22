from __future__ import annotations

from pathlib import Path

from schedule_agent.memory.session_memory import SessionMemoryStore


def main() -> int:
    artifacts = Path("artifacts")
    (artifacts / "traces").mkdir(parents=True, exist_ok=True)
    database_path = artifacts / "lab.db"
    SessionMemoryStore(database_path)
    print(f"Seeded local state at {database_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
