from __future__ import annotations

from pathlib import Path

from scripts import tasks
from scripts.stage_catalog import get_stage


def test_command_for_run_api_uses_python_module_invocation() -> None:
    command = tasks.command_for("run-api", host="0.0.0.0", port=9000)
    assert command[:3] == [tasks.sys.executable, "-m", "uvicorn"]
    assert command[-4:] == ["--host", "0.0.0.0", "--port", "9000"]


def test_command_for_install_web_supports_windows_npm_wrapper() -> None:
    command = tasks.command_for("install-web", npm_executable="npm.cmd")
    assert command == ["npm.cmd", "--prefix", "apps/web", "install"]


def test_init_env_file_copies_template_without_shell_commands(tmp_path: Path) -> None:
    env_example = tmp_path / ".env.example"
    env_example.write_text("LLM_PROVIDER=mock\n", encoding="utf-8")

    env_file = tasks.init_env_file(tmp_path)

    assert env_file.read_text(encoding="utf-8") == "LLM_PROVIDER=mock\n"


def test_clear_lab_artifacts_removes_db_and_traces_cross_platform(tmp_path: Path) -> None:
    artifacts = tmp_path / "artifacts"
    trace_dir = artifacts / "traces"
    trace_dir.mkdir(parents=True)
    db_file = artifacts / "lab.db"
    trace_file = trace_dir / "session.jsonl"
    db_file.write_text("db", encoding="utf-8")
    trace_file.write_text("trace", encoding="utf-8")

    removed = tasks.clear_lab_artifacts(tmp_path)

    assert db_file in removed
    assert trace_file in removed
    assert not db_file.exists()
    assert not trace_file.exists()


def test_stage_catalog_exposes_e2e_mapping_for_validation_and_web() -> None:
    validation = get_stage("stage-05-validation")
    web = get_stage("stage-09-web")

    assert validation.smoke_actions == ("eval",)
    assert validation.tests == ("tests/stage_04_validation",)
    assert web.smoke_actions == ("build-web",)
    assert web.tests == ("tests/web",)
