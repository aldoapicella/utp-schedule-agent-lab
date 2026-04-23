from __future__ import annotations

import json
import re
import unicodedata
from dataclasses import dataclass
from pathlib import Path

SUBJECT_ALIASES: dict[str, tuple[str, ...]] = {
    "5002": ("BD 1", "BASE DATOS 1", "BASE DE DATOS 1"),
    "5003": ("BD 2", "BASE DATOS 2", "BASE DE DATOS 2"),
    "0690": ("REQUISITOS", "INGENIERIA REQUISITOS"),
    "0692": ("CALIDAD", "CALIDAD SOFTWARE"),
    "0687": (
        "ARQUITECTURA DE COMPUTADORA",
        "ORGANIZACION ARQUITECTURA COMPUTADORA",
        "ARQUITECTURA COMP",
    ),
    "0760": ("ARQUITECTURA SOFTWARE",),
    "0755": ("REDES", "REDES 1", "REDES DE COMPUTADORAS"),
    "0801": ("TOPICOS", "TOPICOS ESPECIALES", "TOPICOS ESPECIALES SOFTWARE"),
}


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def default_data_dir() -> Path:
    return _repo_root() / "scenarios" / "utp_semester_planning" / "data"


def normalize_text(value: str) -> str:
    normalized = unicodedata.normalize("NFD", value)
    without_marks = "".join(char for char in normalized if unicodedata.category(char) != "Mn")
    uppercase = without_marks.upper()
    without_punctuation = re.sub(r"[^A-Z0-9]+", " ", uppercase)
    collapsed = re.sub(r"\s+", " ", without_punctuation).strip()

    normalized_words = collapsed
    for source, target in (
        ("ORG", "ORGANIZACION"),
        ("ARQ", "ARQUITECTURA"),
        ("III", "3"),
        ("II", "2"),
        ("IV", "4"),
        ("I", "1"),
    ):
        normalized_words = re.sub(rf"\b{source}\b", target, normalized_words)

    return normalized_words


@dataclass(slots=True)
class Subject:
    subject_id: str
    name: str
    credits: int
    prerequisites: list[str]
    has_lab: bool
    career: str
    term: str


@dataclass(slots=True)
class StudentProfile:
    student_id: str
    name: str
    career: str
    approved_subjects: list[str]
    current_province: str
    max_credits: int


class CatalogStore:
    def __init__(self, data_dir: str | Path | None = None) -> None:
        self.data_dir = Path(data_dir or default_data_dir())
        self.subjects = self._load_subjects()
        self.subjects_by_id = {subject.subject_id: subject for subject in self.subjects}
        self.subject_name_index = {
            normalize_text(subject.name): subject.subject_id for subject in self.subjects
        }
        self.profiles = self._load_profiles()
        self.profiles_by_id = {profile.student_id: profile for profile in self.profiles}
        self.degree_plan = json.loads(
            (self.data_dir / "degree_plan_excerpt.json").read_text(encoding="utf-8")
        )

    def _load_subjects(self) -> list[Subject]:
        payload = json.loads((self.data_dir / "course_catalog.json").read_text(encoding="utf-8"))
        return [Subject(**item) for item in payload]

    def _load_profiles(self) -> list[StudentProfile]:
        payload = json.loads((self.data_dir / "student_profiles.json").read_text(encoding="utf-8"))
        return [StudentProfile(**item) for item in payload]

    def get_profile(self, student_id: str) -> StudentProfile | None:
        return self.profiles_by_id.get(student_id)

    def list_subjects(self, career_code: str, term: str) -> list[Subject]:
        return [
            subject
            for subject in self.subjects
            if subject.career == career_code and subject.term == term
        ]

    def get_subject(self, subject_id: str) -> Subject | None:
        return self.subjects_by_id.get(subject_id)

    def resolve_subject_ids_from_text(self, message: str) -> list[str]:
        normalized = normalize_text(message)
        working_text = normalized
        matched: list[str] = []
        subjects_by_specificity = sorted(
            self.subjects,
            key=lambda subject: len(normalize_text(subject.name)),
            reverse=True,
        )
        for subject in subjects_by_specificity:
            if subject.subject_id in message and subject.subject_id not in matched:
                matched.append(subject.subject_id)
                continue
            normalized_name = normalize_text(subject.name)
            if normalized_name in working_text and subject.subject_id not in matched:
                matched.append(subject.subject_id)
                working_text = working_text.replace(normalized_name, " ")
                continue
            aliases = sorted(
                SUBJECT_ALIASES.get(subject.subject_id, ()),
                key=lambda alias: len(normalize_text(alias)),
                reverse=True,
            )
            for alias in aliases:
                normalized_alias = normalize_text(alias)
                if normalized_alias in working_text and subject.subject_id not in matched:
                    matched.append(subject.subject_id)
                    working_text = working_text.replace(normalized_alias, " ")
                    break
        return matched

    def total_credits(self, subject_ids: list[str]) -> int:
        return sum(self.subjects_by_id[subject_id].credits for subject_id in subject_ids if subject_id in self.subjects_by_id)
