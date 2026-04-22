from __future__ import annotations

from pathlib import Path


def main() -> int:
    artifacts = Path("artifacts")
    (artifacts / "traces").mkdir(parents=True, exist_ok=True)
    print(f"Seeded local artifacts at {artifacts}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
