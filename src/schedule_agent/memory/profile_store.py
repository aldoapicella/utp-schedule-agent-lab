from __future__ import annotations

from schedule_agent.data.catalog import CatalogStore, StudentProfile, default_data_dir


class ProfileStore:
    def __init__(self, data_dir=None) -> None:
        self.catalog = CatalogStore(data_dir or default_data_dir())

    def get_student_profile(self, student_id: str) -> StudentProfile | None:
        return self.catalog.get_profile(student_id)

