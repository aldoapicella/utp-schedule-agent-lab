from __future__ import annotations

from pathlib import Path


class KnowledgeRetriever:
    def __init__(self, docs_dir: str | Path) -> None:
        self.docs_dir = Path(docs_dir)

    def explain(self, topic: str) -> str:
        topic_name = topic.lower().replace(" ", "_")
        path = self.docs_dir / f"{topic_name}.md"
        if path.exists():
            return path.read_text(encoding="utf-8")
        general = self.docs_dir / "lab_domain_rules.md"
        return general.read_text(encoding="utf-8")

