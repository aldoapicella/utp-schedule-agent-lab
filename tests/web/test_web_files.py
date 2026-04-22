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
    assert "[selectedStudent]" in page


def test_dashboard_uses_weekly_schedule_component() -> None:
    page = Path("apps/web/components/dashboard.tsx").read_text(encoding="utf-8")
    schedule = Path("apps/web/components/weekly-schedule.tsx").read_text(encoding="utf-8")
    assert "Horario recomendado" in page
    assert "WeeklySchedule" in page
    assert "Lunes" in schedule
    assert "Materias incluidas" in schedule
    assert "Exportar PNG" in schedule
    assert "Exportar PDF" in schedule
