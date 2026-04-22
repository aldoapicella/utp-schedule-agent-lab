from __future__ import annotations

import argparse
import os
import platform
import shutil
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
    "tests/stage_07_human",
    "tests/web",
]


def _latest_nvm_binary(binary_name: str) -> str | None:
    nvm_root = Path.home() / ".nvm" / "versions" / "node"
    if not nvm_root.exists():
        return None
    candidates = sorted(nvm_root.glob(f"*/bin/{binary_name}"))
    if not candidates:
        return None
    return str(candidates[-1])


def resolve_npm_executable() -> str:
    for candidate in ("npm", "npm.cmd"):
        if shutil.which(candidate):
            return candidate
    nvm_candidate = _latest_nvm_binary("npm")
    if nvm_candidate:
        return nvm_candidate
    raise SystemExit(
        "No se encontró npm en el PATH. Instala Node.js 20+ y vuelve a intentar."
    )


def resolve_node_executable() -> str | None:
    for candidate in ("node", "node.exe"):
        if shutil.which(candidate):
            return candidate
    return _latest_nvm_binary("node")


def python_command(*args: str) -> list[str]:
    return [sys.executable, *args]


def npm_command(*args: str, executable: str | None = None) -> list[str]:
    return [executable or resolve_npm_executable(), *args]


def command_for(
    action: str,
    *,
    npm_executable: str | None = None,
    host: str = "127.0.0.1",
    port: int = 8000,
) -> list[str]:
    if action == "setup":
        return python_command("-m", "pip", "install", "-e", ".[dev]")
    if action == "test":
        return python_command("-m", "pytest", "-q", "-s", *TEST_PATHS)
    if action == "test-core":
        return python_command("-m", "pytest", "tests/core", "-q")
    if action == "run-core":
        return python_command(
            "-m",
            "apps.cli",
            "--mode",
            "core",
            "--sample",
            "scenarios/utp_semester_planning/data/sample_requests.json",
        )
    if action == "run-agent":
        return python_command("-m", "apps.cli", "--mode", "agent")
    if action == "run-api":
        return python_command(
            "-m",
            "uvicorn",
            "apps.api.main:app",
            "--reload",
            "--host",
            host,
            "--port",
            str(port),
        )
    if action == "install-web":
        return npm_command("--prefix", "apps/web", "install", executable=npm_executable)
    if action == "run-web":
        return npm_command("--prefix", "apps/web", "run", "dev", executable=npm_executable)
    if action == "build-web":
        return npm_command(
            "--prefix", "apps/web", "run", "build", executable=npm_executable
        )
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
    if action == "trace":
        return python_command("-m", "schedule_agent.monitoring.trace_viewer")
    if action == "seed":
        return python_command("scripts/seed_data.py")
    raise KeyError(f"Acción no soportada: {action}")


def clear_lab_artifacts(root: Path = ROOT) -> list[Path]:
    removed: list[Path] = []
    db_file = root / "artifacts" / "lab.db"
    if db_file.exists():
        db_file.unlink()
        removed.append(db_file)

    trace_dir = root / "artifacts" / "traces"
    if trace_dir.exists():
        for trace_file in trace_dir.glob("*.jsonl"):
            trace_file.unlink()
            removed.append(trace_file)

    return removed


def init_env_file(root: Path = ROOT, *, overwrite: bool = False) -> Path:
    env_example = root / ".env.example"
    env_file = root / ".env"

    if not env_example.exists():
        raise SystemExit("No existe .env.example en la raíz del repositorio.")

    if env_file.exists() and not overwrite:
        return env_file

    env_file.write_text(env_example.read_text(encoding="utf-8"), encoding="utf-8")
    return env_file


def print_run_ui_instructions() -> None:
    print("Abre dos terminales dentro del repositorio y ejecuta:")
    print(f"  1. {sys.executable} -m scripts.tasks run-api")
    print(f"  2. {sys.executable} -m scripts.tasks run-web")
    print("")
    print("Luego abre http://127.0.0.1:3000 en tu navegador.")


def print_doctor_report() -> None:
    os_name = platform.system() or "Unknown"
    python_version = platform.python_version()
    node_executable = resolve_node_executable()
    npm_executable = None
    try:
        npm_executable = resolve_npm_executable()
    except SystemExit:
        npm_executable = None

    print("Preflight del laboratorio")
    print("-------------------------")
    print(f"Sistema operativo: {os_name}")
    print(f"Python activo: {sys.executable}")
    print(f"Versión de Python: {python_version}")
    print(f"Node.js: {node_executable or 'no encontrado'}")
    print(f"npm: {npm_executable or 'no encontrado'}")
    print(f"Archivo .env: {'presente' if ENV_FILE.exists() else 'faltante'}")
    print(f"Base de datos local: {ARTIFACTS_DIR / 'lab.db'}")
    print("")
    if not node_executable or not npm_executable:
        print("Falta Node.js/npm. Instala Node.js 20+ para usar la web del taller.")
    else:
        print("El entorno base está listo para backend, tests y frontend.")


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
    print(f"Tema del libro: {stage.book_theme}")
    print(f"Resumen: {stage.summary}")
    print(f"Doc: {ROOT / stage.doc_path}")
    print(f"Runtime: {', '.join(stage.runtime_surface)}")
    print(f"Actividad: {stage.activity}")
    print(f"Mensaje: {stage.key_message}")
    print(f"Smoke commands: {', '.join(stage.smoke_actions) or 'none'}")
    print(f"Test paths: {', '.join(stage.tests)}")


def run(command: Sequence[str]) -> int:
    printable = " ".join(command)
    print(f"+ {printable}")
    env = os.environ.copy()
    executable = Path(command[0])
    if executable.is_absolute() and executable.name.startswith("npm"):
        env["PATH"] = f"{executable.parent}:{env.get('PATH', '')}"
    completed = subprocess.run(command, cwd=ROOT, check=False, env=env)
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
    parser = argparse.ArgumentParser(
        description="Runner multiplataforma para UTP Schedule Agent Lab."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("doctor", help="Verifica prerequisitos locales.")
    subparsers.add_parser("list-stages", help="Lista los stages del laboratorio.")

    init_env_parser = subparsers.add_parser(
        "init-env", help="Copia .env.example a .env si no existe."
    )
    init_env_parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Sobrescribe .env si ya existe.",
    )

    for action, help_text in (
        ("setup", "Instala dependencias Python del laboratorio."),
        ("test", "Ejecuta toda la suite de pruebas."),
        ("test-core", "Ejecuta solo las pruebas del core."),
        ("run-core", "Ejecuta el flujo determinista por CLI."),
        ("run-agent", "Ejecuta el agente por CLI."),
        ("install-web", "Instala dependencias del frontend."),
        ("run-web", "Levanta la app web en modo desarrollo."),
        ("build-web", "Compila el frontend de Next.js."),
        ("eval", "Ejecuta la evaluación del agente."),
        ("attack-tests", "Ejecuta pruebas adversariales."),
        ("trace", "Abre el visor de trazas del laboratorio."),
        ("seed", "Regenera datos sintéticos locales."),
        ("reset", "Limpia artefactos y vuelve a sembrar datos."),
        ("run-ui", "Muestra el flujo recomendado para levantar la UI."),
    ):
        subparsers.add_parser(action, help=help_text)

    for action, help_text in (
        ("stage-info", "Muestra metadata didáctica y operativa de un stage."),
        ("stage-test", "Ejecuta la suite principal de un stage."),
        ("stage-e2e", "Ejecuta smoke commands y pruebas del stage."),
    ):
        stage_parser = subparsers.add_parser(action, help=help_text)
        stage_parser.add_argument("stage_id")

    run_api_parser = subparsers.add_parser("run-api", help="Levanta la API FastAPI.")
    run_api_parser.add_argument("--host", default="127.0.0.1")
    run_api_parser.add_argument("--port", type=int, default=8000)

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

    if args.command == "run-ui":
        print_run_ui_instructions()
        return 0

    if args.command == "reset":
        removed = clear_lab_artifacts()
        for path in removed:
            print(f"Eliminado: {path.relative_to(ROOT)}")
        return run(command_for("seed"))

    if args.command == "run-api":
        return run(command_for("run-api", host=args.host, port=args.port))

    return run(command_for(args.command))


if __name__ == "__main__":
    raise SystemExit(main())
