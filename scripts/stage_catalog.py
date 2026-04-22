from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class StageDefinition:
    id: str
    title: str
    duration_minutes: int
    guiding_question: str
    summary: str
    doc_path: str
    tests: tuple[str, ...]
    smoke_actions: tuple[str, ...]


STAGES: tuple[StageDefinition, ...] = (
    StageDefinition(
        id="stage-00-core",
        title="Core determinista",
        duration_minutes=8,
        guiding_question="¿Qué parte del problema debemos resolver sin IA?",
        summary="Motor de horarios, datasets sintéticos y reglas del dominio.",
        doc_path="docs/stages/stage-00-core.md",
        tests=("tests/core",),
        smoke_actions=("seed", "run-core"),
    ),
    StageDefinition(
        id="stage-01-design",
        title="Diseño",
        duration_minutes=10,
        guiding_question="¿Este problema realmente necesita un agente?",
        summary="Goal, non-goals, constraints, risks y criterios de éxito.",
        doc_path="docs/stages/stage-01-design.md",
        tests=("tests/stage_01_design",),
        smoke_actions=("seed",),
    ),
    StageDefinition(
        id="stage-02-tools",
        title="Tools",
        duration_minutes=12,
        guiding_question="¿Qué puede hacer el agente?",
        summary="Catálogo sintético, tools tipadas y un agente simple que las consume.",
        doc_path="docs/stages/stage-02-tools.md",
        tests=("tests/stage_01_tools",),
        smoke_actions=("run-agent",),
    ),
    StageDefinition(
        id="stage-03-orchestration",
        title="Orquestación",
        duration_minutes=12,
        guiding_question="¿Quién decide el siguiente paso?",
        summary="AgentState, planner-executor y flujo explícito de herramientas.",
        doc_path="docs/stages/stage-03-orchestration.md",
        tests=("tests/stage_02_orchestration",),
        smoke_actions=("run-agent",),
    ),
    StageDefinition(
        id="stage-04-memory",
        title="Memoria",
        duration_minutes=8,
        guiding_question="¿Qué debe recordar y qué no?",
        summary="Preferencias de sesión persistidas en SQLite local.",
        doc_path="docs/stages/stage-04-memory.md",
        tests=("tests/stage_03_memory",),
        smoke_actions=("run-agent",),
    ),
    StageDefinition(
        id="stage-05-validation",
        title="Validación",
        duration_minutes=12,
        guiding_question="¿Cómo sabemos que el agente hizo bien su trabajo?",
        summary="Constraints compartidas, métricas y evaluación por dataset.",
        doc_path="docs/stages/stage-05-validation.md",
        tests=("tests/stage_04_validation",),
        smoke_actions=("eval",),
    ),
    StageDefinition(
        id="stage-06-monitoring",
        title="Monitoring",
        duration_minutes=8,
        guiding_question="¿Cómo sabemos qué pasó por dentro?",
        summary="TelemetrySession, trace files y API de observabilidad.",
        doc_path="docs/stages/stage-06-monitoring.md",
        tests=("tests/stage_05_monitoring",),
        smoke_actions=("run-agent", "trace"),
    ),
)

STAGE_MAP = {stage.id: stage for stage in STAGES}


def get_stage(stage_id: str) -> StageDefinition:
    try:
        return STAGE_MAP[stage_id]
    except KeyError as exc:
        available = ", ".join(stage.id for stage in STAGES)
        raise KeyError(f"Stage desconocido '{stage_id}'. Disponibles: {available}") from exc
