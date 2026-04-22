from __future__ import annotations

import argparse
import platform
import subprocess
import sys
from pathlib import Path
from typing import Sequence

from scripts.stage_catalog import STAGES, get_stage


ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS_DIR = ROOT / "artifacts"
ENV_FILE = ROOT / ".env"
TEST_PATHS = [
    "tests/core",
    "tests/stage_01_design",
    "tests/stage_01_tools",
    "tests/stage_02_orchestration",
    "tests/stage_03_memory",
    "tests/stage_04_validation",
    "tests/stage_05_monitoring",
    "tests/stage_06_security",
]


def python_command(*args: str) -> list[str]:
    return [sys.executable, *args]


def command_for(action: str) -> list[str]:
    if action == "setup":
        return python_command("-m", "pip", "install", "-e", ".[dev]")
    if action == "test":
        return python_command("-m", "pytest", "-q", "-s", *TEST_PATHS)
    if action == "test-core":
        return python_command("-m", "pytest", "tests/core", "-q")
    if action == "run-core":
        return python_command("-m", "apps.cli", "--mode", "core")
    if action == "run-agent":
        return python_command("-m", "apps.cli", "--mode", "agent")
    if action == "eval":
        return python_command(
            "scripts/run_eval.py",
            "--dataset",
            "src/schedule_agent/validation/datasets/eval_set.jsonl",
        )
    if action == "attack-tests":
        return python_command(
            "scripts/run_attack_tests.py",
            "--dataset",
            "src/schedule_agent/validation/datasets/adversarial_set.jsonl",
        )
    if action == "run-api":
        return python_command(
            "-m",
            "uvicorn",
            "apps.api.main:app",
            "--reload",
            "--host",
            "127.0.0.1",
            "--port",
            "8000",
        )
    if action == "trace":
        return python_command("-m", "schedule_agent.monitoring.trace_viewer")
    if action == "seed":
        return python_command("scripts/seed_data.py")
    raise KeyError(f"Acción no soportada: {action}")


def clear_lab_artifacts(root: Path = ROOT) -> list[Path]:
    removed: list[Path] = []
    artifacts_dir = root / "artifacts"
    if artifacts_dir.exists():
        for path in sorted(artifacts_dir.rglob("*"), reverse=True):
            if path.is_file():
                path.unlink()
                removed.append(path)
            elif path.is_dir():
                try:
                    path.rmdir()
                except OSError:
                    pass
        try:
            artifacts_dir.rmdir()
        except OSError:
            pass
    return removed


def init_env_file(root: Path = ROOT, *, overwrite: bool = False) -> Path:
    env_example = root / ".env.example"
    env_file = root / ".env"
    if env_file.exists() and not overwrite:
        return env_file
    env_file.write_text(env_example.read_text(encoding="utf-8"), encoding="utf-8")
    return env_file


def print_doctor_report() -> None:
    print("Preflight del laboratorio")
    print("-------------------------")
    print(f"Sistema operativo: {platform.system() or 'Unknown'}")
    print(f"Python activo: {sys.executable}")
    print(f"Versión de Python: {platform.python_version()}")
    print(f"Archivo .env: {'presente' if ENV_FILE.exists() else 'faltante'}")
    print(f"Artifacts: {ARTIFACTS_DIR}")


def print_stage_list() -> None:
    print("Stages del laboratorio")
    print("----------------------")
    for stage in STAGES:
        print(f"{stage.id}: {stage.title} ({stage.duration_minutes} min)")


def print_stage_info(stage_id: str) -> None:
    stage = get_stage(stage_id)
    print(f"{stage.id} - {stage.title}")
    print("-" * (len(stage.id) + len(stage.title) + 3))
    print(f"Pregunta guía: {stage.guiding_question}")
    print(f"Resumen: {stage.summary}")
    print(f"Doc: {ROOT / stage.doc_path}")
    print(f"Smoke commands: {', '.join(stage.smoke_actions)}")
    print(f"Test paths: {', '.join(stage.tests)}")


def run(command: Sequence[str]) -> int:
    print(f"+ {' '.join(command)}")
    completed = subprocess.run(command, cwd=ROOT, check=False)
    return completed.returncode


def run_stage_tests(stage_id: str) -> int:
    stage = get_stage(stage_id)
    return run(python_command("-m", "pytest", "-q", "-s", *stage.tests))


def run_stage_e2e(stage_id: str) -> int:
    stage = get_stage(stage_id)
    for action in stage.smoke_actions:
        result = run(command_for(action))
        if result != 0:
            return result
    return run_stage_tests(stage_id)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Runner multiplataforma para los primeros stages.")
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("doctor")
    subparsers.add_parser("list-stages")
    init_env_parser = subparsers.add_parser("init-env")
    init_env_parser.add_argument("--overwrite", action="store_true")
    for action in (
        "setup",
        "test",
        "test-core",
        "run-core",
        "run-agent",
        "run-api",
        "eval",
        "attack-tests",
        "trace",
        "seed",
        "reset",
    ):
        subparsers.add_parser(action)
    for action in ("stage-info", "stage-test", "stage-e2e"):
        stage_parser = subparsers.add_parser(action)
        stage_parser.add_argument("stage_id")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "doctor":
        print_doctor_report()
        return 0
    if args.command == "list-stages":
        print_stage_list()
        return 0
    if args.command == "init-env":
        env_file = init_env_file(overwrite=args.overwrite)
        print(f"Archivo listo: {env_file}")
        return 0
    if args.command == "stage-info":
        print_stage_info(args.stage_id)
        return 0
    if args.command == "stage-test":
        return run_stage_tests(args.stage_id)
    if args.command == "stage-e2e":
        return run_stage_e2e(args.stage_id)
    if args.command == "reset":
        removed = clear_lab_artifacts()
        for path in removed:
            print(f"Eliminado: {path.relative_to(ROOT)}")
        return run(command_for("seed"))
    return run(command_for(args.command))


if __name__ == "__main__":
    raise SystemExit(main())
