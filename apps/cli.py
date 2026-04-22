from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path

from schedule_calculator.adapters.in_memory_repository import InMemoryGroupCatalogRepository
from schedule_calculator.application.scheduler import SchedulerService
from schedule_calculator.domain.models import ScheduleRequest
from schedule_calculator.formatters import format_schedule_summary
from schedule_agent.orchestration.simple_agent import UTPPlanningAgent


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="UTP Schedule Agent Lab CLI")
    parser.add_argument("--mode", choices=["core", "agent"], default="agent")
    parser.add_argument(
        "--sample",
        default="scenarios/utp_semester_planning/data/sample_requests.json",
        help="Path to sample requests JSON.",
    )
    return parser


def _run_core(sample_path: str) -> int:
    data_dir = Path("scenarios/utp_semester_planning/data")
    repository = InMemoryGroupCatalogRepository.from_json(data_dir / "group_catalog.json")
    scheduler = SchedulerService(repository)
    sample = json.loads(Path(sample_path).read_text(encoding="utf-8"))[0]
    request = ScheduleRequest(
        desired_subjects=["5003", "0692", "0687"],
        required_subjects=["5003"],
        available_start=datetime.strptime("17:00", "%H:%M").time(),
        available_end=datetime.strptime("22:30", "%H:%M").time(),
        desired_province="PANAMÁ",
    )
    result = scheduler.find_best_schedule(request)
    print(format_schedule_summary(result))
    print(f"Sample message: {sample['message']}")
    return 0


def _run_agent(sample_path: str) -> int:
    agent = UTPPlanningAgent()
    samples = json.loads(Path(sample_path).read_text(encoding="utf-8"))
    for sample in samples:
        result = agent.respond(
            student_id=sample["student_id"],
            message=sample["message"],
            term=sample["term"],
        )
        print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    if args.mode == "core":
        return _run_core(args.sample)
    return _run_agent(args.sample)


if __name__ == "__main__":
    raise SystemExit(main())
