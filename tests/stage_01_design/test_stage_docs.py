from __future__ import annotations

from pathlib import Path

from scripts.stage_catalog import STAGES


def test_stage_catalog_covers_ten_stages() -> None:
    assert len(STAGES) == 10
    assert STAGES[0].id == "stage-00-core"
    assert STAGES[-1].id == "stage-09-web"


def test_every_stage_doc_has_teaching_sections_and_mermaid() -> None:
    required_sections = (
        "## Pregunta guía",
        "## Conceptos a explicar",
        "## Ejecución",
        "## Actividad",
        "## Señal de éxito",
        "```mermaid",
    )

    for stage in STAGES:
        doc = Path(stage.doc_path).read_text(encoding="utf-8")
        for section in required_sections:
            assert section in doc, f"{stage.id} missing section {section}"


def test_presentation_structure_documents_branch_and_tag_strategy() -> None:
    presentation = Path("docs/presentation_structure.md").read_text(encoding="utf-8")
    assert "student-start" in presentation
    assert "instructor-solution" in presentation
    assert "stage-00-core" in presentation
    assert "stage-09-web" in presentation
    assert "```mermaid" in presentation


def test_scenario_and_design_docs_are_present_for_stage_01() -> None:
    scenario = Path("scenarios/utp_semester_planning/spec.md").read_text(encoding="utf-8")
    design = Path("src/schedule_agent/design/scenario_spec.md").read_text(encoding="utf-8")
    constraints = Path("src/schedule_agent/design/constraints.md").read_text(encoding="utf-8")
    architecture = Path("src/schedule_agent/design/architecture.md").read_text(encoding="utf-8")

    assert "## Objetivo del agente" in scenario
    assert "```mermaid" in scenario
    assert "## Success Criteria" in design
    assert "## Teaching Lens" in constraints
    assert "## Teaching Message" in architecture
