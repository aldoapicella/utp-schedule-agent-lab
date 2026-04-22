from __future__ import annotations

from dataclasses import asdict

from schedule_agent.data.catalog import CatalogStore


class CatalogTools:
    def __init__(self, catalog: CatalogStore, group_repository) -> None:
        self.catalog = catalog
        self.group_repository = group_repository

    def get_student_profile(self, student_id: str) -> dict | None:
        profile = self.catalog.get_profile(student_id)
        return asdict(profile) if profile else None

    def list_available_subjects(self, career_code: str, term: str) -> list[dict]:
        return [asdict(subject) for subject in self.catalog.list_subjects(career_code, term)]

    def get_subject_details(self, subject_id: str) -> dict | None:
        subject = self.catalog.get_subject(subject_id)
        return asdict(subject) if subject else None

    def get_available_groups(self, subject_ids: list[str], province: str) -> dict[str, list[dict]]:
        groups: dict[str, list[dict]] = {}
        for subject_id in subject_ids:
            groups[subject_id] = [
                {
                    "group_code": group.group_code,
                    "subject_id": group.subject_id,
                    "province": group.province,
                    "subject_name": group.subject_name,
                    "hour_code": group.hour_code,
                }
                for group in self.group_repository.list_groups_for_subject(subject_id)
                if group.province.upper() == province.upper()
                or all(session.classroom.upper() == "VVIRT" for session in group.sessions)
            ]
        return groups

    def check_prerequisites(self, student_id: str, subject_ids: list[str]) -> dict[str, list[str]]:
        profile = self.catalog.get_profile(student_id)
        if profile is None:
            return {subject_id: ["UNKNOWN_STUDENT"] for subject_id in subject_ids}
        missing: dict[str, list[str]] = {}
        approved = set(profile.approved_subjects)
        for subject_id in subject_ids:
            subject = self.catalog.get_subject(subject_id)
            if subject is None:
                missing[subject_id] = ["UNKNOWN_SUBJECT"]
                continue
            missing_prereqs = [prereq for prereq in subject.prerequisites if prereq not in approved]
            if missing_prereqs:
                missing[subject_id] = missing_prereqs
        return missing

