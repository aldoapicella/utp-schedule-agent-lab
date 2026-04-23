from __future__ import annotations

from schedule_agent.data.catalog import CatalogStore
from schedule_agent.orchestration.simple_agent import UTPPlanningAgent


def test_catalog_resolves_subject_variants_from_natural_text() -> None:
    catalog = CatalogStore()

    subject_ids = catalog.resolve_subject_ids_from_text(
        "Quiero tomar base de datos 2, calidad de software y organizacion y arquitectura de computadora."
    )

    assert set(subject_ids) == {"5003", "0692", "0687"}


def test_catalog_resolves_short_aliases_from_custom_prompt() -> None:
    catalog = CatalogStore()

    subject_ids = catalog.resolve_subject_ids_from_text(
        "Quiero tomar BD II, redes de computadoras y topicos especiales."
    )

    assert set(subject_ids) == {"5003", "0755", "0801"}


def test_agent_returns_warning_when_subjects_are_not_recognized() -> None:
    agent = UTPPlanningAgent()

    response = agent.respond(
        student_id="student_software_01",
        term="2026-1",
        message="Quiero tomar Inteligencia Artificial y Ética Profesional.",
    )

    assert response["recommended_schedule"] is None
    assert response["assistant_message"] == "No pude identificar las materias de tu solicitud."
    assert any("No pude identificar materias concretas" in warning for warning in response["warnings"])
