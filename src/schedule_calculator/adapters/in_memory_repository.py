from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from schedule_calculator.domain.models import CourseGroup, SessionRecord


def _parse_time(value: str):
    return datetime.strptime(value, "%H:%M").time()


@dataclass
class InMemoryGroupCatalogRepository:
    groups_by_subject: dict[str, list[CourseGroup]]

    @classmethod
    def from_json(cls, path: str | Path) -> "InMemoryGroupCatalogRepository":
        payload = json.loads(Path(path).read_text(encoding="utf-8"))
        groups_by_subject: dict[str, list[CourseGroup]] = {}
        for item in payload:
            group = CourseGroup(
                group_code=item["group_code"],
                subject_id=item["subject_id"],
                province=item["province"],
                subject_name=item.get("subject_name", ""),
                hour_code=item.get("hour_code", ""),
                sessions=[
                    SessionRecord(
                        day=session["day"],
                        subject=session.get("subject", item["subject_id"]),
                        session_type=session.get("session_type", "Theory"),
                        classroom=session.get("classroom", ""),
                        lab_code=session.get("lab_code"),
                        start_time=_parse_time(session["start_time"]),
                        end_time=_parse_time(session["end_time"]),
                    )
                    for session in item["sessions"]
                ],
            )
            groups_by_subject.setdefault(group.subject_id, []).append(group)
        return cls(groups_by_subject)

    def list_groups_for_subject(self, subject_id: str) -> list[CourseGroup]:
        return list(self.groups_by_subject.get(subject_id, []))

