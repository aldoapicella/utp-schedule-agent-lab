from __future__ import annotations

import argparse

from schedule_agent.orchestration.simple_agent import UTPPlanningAgent
from schedule_agent.validation.evaluator import EvaluationHarness


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", required=True)
    args = parser.parse_args(argv)

    harness = EvaluationHarness(UTPPlanningAgent())
    summary = harness.run(args.dataset)
    print("Evaluation summary")
    print("------------------")
    print(f"Cases: {int(summary['cases'])}")
    print(f"Hard constraint pass rate: {summary['hard_constraint_pass_rate']:.0%}")
    print(f"Prerequisite accuracy: {summary['prerequisite_accuracy']:.0%}")
    print(f"Conflict rate: {summary['schedule_conflict_rate']:.0%}")
    print(f"Human review precision: {summary['human_review_precision']:.0%}")
    print(f"Average tool calls: {summary['average_tool_calls']:.1f}")
    print(f"Average latency: {summary['average_latency_ms'] / 1000:.1f}s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

