from __future__ import annotations


def summarize_metrics(results: list[dict]) -> dict[str, float]:
    total = len(results) or 1
    hard_pass = sum(1 for result in results if result["passed"])
    prerequisite_accuracy = sum(1 for result in results if result["prereq_ok"]) / total
    conflict_rate = sum(1 for result in results if result["conflict"]) / total
    human_review_precision = sum(1 for result in results if result["human_review_ok"]) / total
    average_tool_calls = sum(result["tool_calls"] for result in results) / total
    average_latency_ms = sum(result["latency_ms"] for result in results) / total
    return {
        "cases": float(len(results)),
        "hard_constraint_pass_rate": hard_pass / total,
        "prerequisite_accuracy": prerequisite_accuracy,
        "schedule_conflict_rate": conflict_rate,
        "human_review_precision": human_review_precision,
        "average_tool_calls": average_tool_calls,
        "average_latency_ms": average_latency_ms,
    }

