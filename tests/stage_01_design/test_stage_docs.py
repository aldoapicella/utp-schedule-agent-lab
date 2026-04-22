from __future__ import annotations

from pathlib import Path

from scripts.stage_catalog import STAGES


def test_stage_catalog_exposes_core_and_design() -> None:
    assert [stage.id for stage in STAGES] == ["stage-00-core", "stage-01-design"]


def test_design_docs_exist_with_required_sections() -> None:
    scenario = Path("src/schedule_agent/design/scenario_spec.md").read_text(encoding="utf-8")
    constraints = Path("src/schedule_agent/design/constraints.md").read_text(encoding="utf-8")
    architecture = Path("src/schedule_agent/design/architecture.md").read_text(encoding="utf-8")

    assert "## Goal" in scenario
    assert "## Non-goals" in scenario
    assert "## Hard constraints" in scenario
    assert "## Teaching Lens" in constraints
    assert "```mermaid" in architecture
