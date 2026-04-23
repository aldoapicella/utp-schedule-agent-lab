from __future__ import annotations

import re
from typing import Any

from schedule_agent.data.catalog import CatalogStore, normalize_text

PROVINCES = [
    "PANAMÁ OESTE",
    "PANAMA OESTE",
    "PANAMÁ",
    "PANAMA",
    "CHIRIQUÍ",
    "CHIRIQUI",
    "VERAGUAS",
    "COCLÉ",
    "COCLE",
    "AZUERO",
]

DAY_ALIASES = {
    "LUNES": "MONDAY",
    "MARTES": "TUESDAY",
    "MIERCOLES": "WEDNESDAY",
    "JUEVES": "THURSDAY",
    "VIERNES": "FRIDAY",
    "SABADO": "SATURDAY",
    "DOMINGO": "SUNDAY",
}


class PreferenceExtractor:
    def __init__(self, catalog: CatalogStore) -> None:
        self.catalog = catalog

    def extract(self, message: str, previous_memory: dict[str, Any] | None = None) -> dict[str, Any]:
        previous_memory = previous_memory or {}
        preferences = {
            "available_start": previous_memory.get("available_start", "08:00"),
            "available_end": previous_memory.get("available_end", "22:30"),
            "avoid_days": list(previous_memory.get("avoid_days", [])),
            "required_subjects": [],
            "desired_subjects": [],
        }
        for key in ("desired_province", "preferred_shift", "max_credits"):
            value = previous_memory.get(key)
            if value is not None:
                preferences[key] = value

        normalized = normalize_text(message)
        for day_text, day_code in DAY_ALIASES.items():
            if (
                f"NO PUEDO {day_text}" in normalized
                or f"NO PUEDO LOS {day_text}" in normalized
                or f"EVITAR {day_text}" in normalized
                or f"NO {day_text}" in normalized
                or f"SIN {day_text}" in normalized
            ):
                preferences["avoid_days"] = sorted(set([*preferences["avoid_days"], day_code]))
        if (
            "DESPUES DE LAS 5" in normalized
            or "DESPUES DE 5" in normalized
            or "PREFERENCIA DE NOCHE" in normalized
            or "PREFIERO NOCHE" in normalized
            or "NOCTURNO" in normalized
        ):
            preferences["available_start"] = "17:00"
            preferences["preferred_shift"] = "EVENING"
        if "TRABAJO HASTA LAS 5" in normalized or "TRABAJO DE 8 A 5" in normalized:
            preferences["available_start"] = "17:00"
            preferences["preferred_shift"] = "EVENING"
        if "ANTES DE LAS 5" in normalized:
            preferences["available_end"] = "17:00"

        count_match = re.search(r"(\d+)\s+MATERIAS", normalized)
        if count_match:
            preferences["max_subjects"] = int(count_match.group(1))

        for province in PROVINCES:
            if province in normalized:
                canonical = "PANAMÁ OESTE" if "OESTE" in province else province.replace("PANAMA", "PANAMÁ")
                preferences["desired_province"] = canonical
                break

        matched_subjects = self.catalog.resolve_subject_ids_from_text(message)
        if matched_subjects:
            preferences["desired_subjects"] = matched_subjects
            if "OBLIGATORIA" in normalized or "OBLIGATORIO" in normalized:
                preferences["required_subjects"] = [matched_subjects[0]]

        return preferences
