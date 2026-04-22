from __future__ import annotations

from pathlib import Path


def test_readme_documents_cross_platform_workshop_setup() -> None:
    readme = Path("README.md").read_text(encoding="utf-8")
    assert "Windows PowerShell" in readme
    assert "macOS / Linux" in readme
    assert "python -m scripts.tasks setup" in readme
    assert "python -m scripts.tasks run-api" in readme
    assert "python -m scripts.tasks run-web" in readme


def test_makefile_uses_python_task_runner_as_single_source_of_truth() -> None:
    makefile = Path("Makefile").read_text(encoding="utf-8")
    assert "TASKS := $(PYTHON) -m scripts.tasks" in makefile
    assert "$(TASKS) reset" in makefile
