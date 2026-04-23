from __future__ import annotations

from pathlib import Path


def test_dashboard_contains_required_panels() -> None:
    page = Path("apps/web/components/dashboard.tsx").read_text(encoding="utf-8")
    assert "Chat del estudiante" in page
    assert "Recomendación del agente" in page
    assert "Memoria y validación" in page
    assert "Llamadas a tools y trazas" in page


def test_dashboard_resets_session_when_profile_changes() -> None:
    page = Path("apps/web/components/dashboard.tsx").read_text(encoding="utf-8")
    assert "setResponse(null);" in page
    assert "setTrace([]);" in page
    assert "[selectedStudent, term]" in page


def test_dashboard_starts_fresh_request_on_submit() -> None:
    page = Path("apps/web/components/dashboard.tsx").read_text(encoding="utf-8")
    assert "session_id: sessionId ?? undefined" not in page
    assert "setResponse(null);" in page
    assert "setTrace([]);" in page
    assert "student_id: selectedStudent" in page
    assert "message: trimmedMessage" in page


def test_dashboard_surfaces_submitted_prompt_and_warnings() -> None:
    page = Path("apps/web/components/dashboard.tsx").read_text(encoding="utf-8")
    styles = Path("apps/web/app/globals.css").read_text(encoding="utf-8")
    assert "Solicitud enviada" in page
    assert "Solicitud procesada" in page
    assert "warning-banner" in page
    assert ".warning-banner" in styles
    assert ".request-preview-card" in styles


def test_dashboard_surfaces_partial_schedule_status() -> None:
    page = Path("apps/web/components/dashboard.tsx").read_text(encoding="utf-8")
    assert "Alternativa parcial" in page
    assert "Sin combinación" in page
    assert "Horario completo" in page
    assert "Cobertura" in page


def test_dashboard_uses_weekly_schedule_component() -> None:
    page = Path("apps/web/components/dashboard.tsx").read_text(encoding="utf-8")
    schedule = Path("apps/web/components/weekly-schedule.tsx").read_text(encoding="utf-8")
    assert "Horario recomendado" in page
    assert "WeeklySchedule" in page
    assert "Lunes" in schedule
    assert "Materias incluidas" in schedule
    assert "Exportar PNG" in schedule
    assert "Exportar PDF" in schedule
