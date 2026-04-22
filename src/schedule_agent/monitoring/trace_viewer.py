from __future__ import annotations

import json
from pathlib import Path


def iter_traces(trace_dir: str | Path = "artifacts/traces") -> list[dict]:
    items: list[dict] = []
    for path in sorted(Path(trace_dir).glob("*.jsonl")):
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                items.append(json.loads(line))
    return items


def main() -> int:
    traces = iter_traces()
    if not traces:
        print("No traces found.")
        return 0
    for trace in traces[-20:]:
        print(f"{trace['timestamp']} {trace['event']} {trace.get('tool', '')}".rstrip())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
