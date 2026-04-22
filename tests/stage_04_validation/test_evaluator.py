from __future__ import annotations

from schedule_agent.orchestration.simple_agent import UTPPlanningAgent
from schedule_agent.validation.evaluator import EvaluationHarness


def test_evaluation_harness_returns_summary_metrics() -> None:
    harness = EvaluationHarness(UTPPlanningAgent())
    summary = harness.run("src/schedule_agent/validation/datasets/eval_set.jsonl")

    assert summary["cases"] == 3
    assert 0 <= summary["hard_constraint_pass_rate"] <= 1
    assert 0 <= summary["human_review_precision"] <= 1
