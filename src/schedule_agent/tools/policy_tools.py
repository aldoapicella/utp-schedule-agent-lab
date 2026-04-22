from __future__ import annotations

from schedule_agent.knowledge.retriever import KnowledgeRetriever


class PolicyTools:
    def __init__(self, retriever: KnowledgeRetriever) -> None:
        self.retriever = retriever

    def explain_academic_policy(self, topic: str) -> dict:
        return {"topic": topic, "explanation": self.retriever.explain(topic)}

