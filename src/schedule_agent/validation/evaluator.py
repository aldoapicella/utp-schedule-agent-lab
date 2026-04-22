from __future__ import annotations

import json
import time
from pathlib import Path

from schedule_agent.orchestration.simple_agent import UTPPlanningAgent
from schedule_agent.validation.metrics import summarize_metrics


class EvaluationHarness:
    def __init__(self, agent: UTPPlanningAgent) -> None:
        self.agent = agent

    def run(self, dataset_path: str | Path) -> dict:
        rows = []
        for line in Path(dataset_path).read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            case = json.loads(line)
            started = time.perf_counter()
            response = self.agent.respond(
                student_id=case["student_id"],
                message=case["request"],
                term=case.get("term", "2026-1"),
            )
            latency_ms = int((time.perf_counter() - started) * 1000)
            schedule = response["recommended_schedule"] or {"chosen_enrollments": []}
            enrolled_ids = [item["subject_id"] for item in schedule.get("chosen_enrollments", [])]
            validation = response["validation_report"]["hard_constraints"]
            expected = case["expected"]
            rows.append(
                {
                    "passed": all(validation.values()) and all(
                        subject in enrolled_ids for subject in expected.get("must_include", [])
                    ),
                    "prereq_ok": validation.get("prerequisites_satisfied", False),
                    "conflict": not validation.get("no_conflicts", False),
                    "human_review_ok": bool(response["human_review"]) == expected.get("human_review_required", False),
                    "tool_calls": len(response["tool_calls"]),
                    "latency_ms": latency_ms,
                }
            )
        return summarize_metrics(rows)
