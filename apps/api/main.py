from __future__ import annotations

import json
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from apps.api.schemas import (
    AgentChatRequest,
    AgentChatResponse,
    HumanReviewRequest,
    HumanReviewTicketModel,
    SessionStateResponse,
)
from schedule_agent.data.catalog import default_data_dir
from schedule_agent.orchestration.simple_agent import UTPPlanningAgent

app = FastAPI(title="UTP Schedule Agent Lab")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

agent = UTPPlanningAgent()


@app.get("/api/v1/catalog/subjects")
def list_subjects(career: str = "ING_SOFTWARE", term: str = "2026-1") -> list[dict]:
    return agent.catalog_tools.list_available_subjects(career, term)


@app.post("/api/v1/agent/respond", response_model=AgentChatResponse)
def respond(request: AgentChatRequest) -> AgentChatResponse:
    return AgentChatResponse.model_validate(
        agent.respond(
            session_id=request.session_id,
            student_id=request.student_id,
            message=request.message,
            term=request.term,
            career=request.career,
        )
    )


@app.get("/api/v1/sessions/{session_id}", response_model=SessionStateResponse)
def get_session(session_id: str) -> SessionStateResponse:
    state = agent.memory_store.load_state(session_id)
    return SessionStateResponse(session_id=session_id, state=state)


@app.get("/api/v1/sessions/{session_id}/trace")
def get_session_trace(session_id: str) -> list[dict]:
    trace_path = Path(agent.trace_dir) / f"{session_id}.jsonl"
    if not trace_path.exists():
        return []
    return [
        json.loads(line)
        for line in trace_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


@app.post("/api/v1/human-review", response_model=HumanReviewTicketModel)
def request_human_review(request: HumanReviewRequest) -> HumanReviewTicketModel:
    ticket = agent.human_tools.request_human_review(request.reason, request.payload)
    return HumanReviewTicketModel.model_validate(ticket)


@app.get("/api/v1/student-profiles")
def list_student_profiles() -> list[dict]:
    payload = json.loads((Path(default_data_dir()) / "student_profiles.json").read_text(encoding="utf-8"))
    return payload
