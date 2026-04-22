from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class StageDefinition:
    id: str
    title: str
    duration_minutes: int
    guiding_question: str
    book_theme: str
    summary: str
    doc_path: str
    tests: tuple[str, ...]
    smoke_actions: tuple[str, ...]
    runtime_surface: tuple[str, ...]
    activity: str
    key_message: str


STAGES: tuple[StageDefinition, ...] = (
    StageDefinition(
        id="stage-00-core",
        title="Core determinista",
        duration_minutes=8,
        guiding_question="¿Qué parte del problema debemos resolver sin IA?",
        book_theme="Deterministic systems before agent autonomy",
        summary="El laboratorio arranca con el motor de horarios, datos sintéticos y reglas duras ya verificables.",
        doc_path="docs/stages/stage-00-core.md",
        tests=("tests/core",),
        smoke_actions=("seed", "run-core"),
        runtime_surface=("CLI",),
        activity="Ejecutar el core y confirmar que el horario sale sin choques antes de hablar de agentes.",
        key_message="Antes de construir un agente, necesitamos un sistema que sepa hacer algo correctamente.",
    ),
    StageDefinition(
        id="stage-01-design",
        title="Diseño",
        duration_minutes=10,
        guiding_question="¿Este problema realmente necesita un agente?",
        book_theme="System design and autonomy boundaries",
        summary="Define goal, non-goals, restricciones, riesgos y criterios de éxito antes de escribir lógica agentic.",
        doc_path="docs/stages/stage-01-design.md",
        tests=("tests/stage_01_design",),
        smoke_actions=("seed",),
        runtime_surface=("Markdown specs",),
        activity="Leer `scenario_spec.md` y completar una restricción faltante con el grupo.",
        key_message="El diseño define los límites de la autonomía.",
    ),
    StageDefinition(
        id="stage-02-tools",
        title="Tools",
        duration_minutes=12,
        guiding_question="¿Qué puede hacer el agente?",
        book_theme="Tool use with typed contracts",
        summary="Las capacidades del agente se encapsulan en tools tipadas y observables.",
        doc_path="docs/stages/stage-02-tools.md",
        tests=("tests/stage_01_tools",),
        smoke_actions=("run-agent",),
        runtime_surface=("CLI", "FastAPI"),
        activity="Implementar `check_prerequisites()` o `calculate_best_schedule()` con contrato claro.",
        key_message="Las tools convierten lenguaje natural en acciones controladas.",
    ),
    StageDefinition(
        id="stage-03-orchestration",
        title="Orquestación",
        duration_minutes=12,
        guiding_question="¿Quién decide el siguiente paso?",
        book_theme="Planner-executor and controlled loops",
        summary="El agente sigue un flujo explícito para extraer, validar, calcular y responder.",
        doc_path="docs/stages/stage-03-orchestration.md",
        tests=("tests/stage_02_orchestration",),
        smoke_actions=("run-agent",),
        runtime_surface=("CLI", "FastAPI"),
        activity="Completar el flujo `extract -> check -> calculate -> validate -> respond`.",
        key_message="Sin orquestación, el agente improvisa.",
    ),
    StageDefinition(
        id="stage-04-memory",
        title="Memoria",
        duration_minutes=8,
        guiding_question="¿Qué debe recordar y qué no?",
        book_theme="Session memory and bounded context retention",
        summary="La memoria conserva preferencias útiles y elimina secretos o instrucciones inseguras.",
        doc_path="docs/stages/stage-04-memory.md",
        tests=("tests/stage_03_memory",),
        smoke_actions=("run-agent",),
        runtime_surface=("CLI", "FastAPI"),
        activity="Probar que el agente recuerde `no puedo viernes` en el siguiente turno.",
        key_message="Memoria útil no es guardar todo; es guardar lo necesario con límites.",
    ),
    StageDefinition(
        id="stage-05-validation",
        title="Validación",
        duration_minutes=12,
        guiding_question="¿Cómo sabemos que el agente hizo bien su trabajo?",
        book_theme="Evaluation, metrics, and regression testing",
        summary="El laboratorio usa datasets, métricas y regresión para medir confiabilidad.",
        doc_path="docs/stages/stage-05-validation.md",
        tests=("tests/stage_04_validation",),
        smoke_actions=("eval",),
        runtime_surface=("CLI",),
        activity="Ejecutar la evaluación y discutir qué métrica falta para producción.",
        key_message="Un agente sin evaluación es una demo, no un sistema.",
    ),
    StageDefinition(
        id="stage-06-monitoring",
        title="Monitoring",
        duration_minutes=8,
        guiding_question="¿Cómo sabemos qué pasó por dentro?",
        book_theme="Observability and production tracing",
        summary="Trazas, logs estructurados y timeline permiten depurar el comportamiento agentic.",
        doc_path="docs/stages/stage-06-monitoring.md",
        tests=("tests/stage_05_monitoring",),
        smoke_actions=("run-agent", "trace"),
        runtime_surface=("CLI", "FastAPI", "Dashboard"),
        activity="Abrir las trazas y ubicar una llamada a tool, su latencia y su resultado.",
        key_message="Observabilidad es el debugger de los agentes.",
    ),
    StageDefinition(
        id="stage-07-security",
        title="Security",
        duration_minutes=10,
        guiding_question="¿Qué pasa si el usuario intenta romper el sistema?",
        book_theme="Protecting agentic systems",
        summary="Se endurece el agente contra prompt injection, mal uso de tools y filtración de PII.",
        doc_path="docs/stages/stage-07-security.md",
        tests=("tests/stage_06_security",),
        smoke_actions=("attack-tests",),
        runtime_surface=("CLI", "FastAPI"),
        activity="Ejecutar ataques básicos y revisar por qué el agente no debe guardar credenciales.",
        key_message="La autonomía sin permisos es riesgo.",
    ),
    StageDefinition(
        id="stage-08-human-collaboration",
        title="Human collaboration",
        duration_minutes=8,
        guiding_question="¿Cuándo debe intervenir una persona?",
        book_theme="Human-in-the-loop and escalation",
        summary="El agente identifica casos ambiguos o inseguros y los envía a revisión humana.",
        doc_path="docs/stages/stage-08-human-collaboration.md",
        tests=("tests/stage_07_human",),
        smoke_actions=("run-agent",),
        runtime_surface=("CLI", "FastAPI", "Dashboard"),
        activity="Forzar un caso con prerrequisito faltante y revisar el ticket en la cola.",
        key_message="El agente confiable no es el que nunca escala; es el que escala bien.",
    ),
    StageDefinition(
        id="stage-09-web",
        title="Web app",
        duration_minutes=10,
        guiding_question="¿Cómo hacemos visible y utilizable el sistema completo?",
        book_theme="User-facing integration and operational UX",
        summary="La web integra chat, horario, tool calls, memoria, validación y exportación de horario.",
        doc_path="docs/stages/stage-09-web.md",
        tests=("tests/web",),
        smoke_actions=("build-web",),
        runtime_surface=("FastAPI", "Next.js Dashboard"),
        activity="Levantar la UI y recorrer el flujo feliz y el handoff humano.",
        key_message="La interfaz final debe mostrar decisiones, límites y evidencia, no solo una respuesta bonita.",
    ),
)

STAGE_MAP = {stage.id: stage for stage in STAGES}


def get_stage(stage_id: str) -> StageDefinition:
    try:
        return STAGE_MAP[stage_id]
    except KeyError as exc:
        available = ", ".join(stage.id for stage in STAGES)
        raise KeyError(f"Stage desconocido '{stage_id}'. Disponibles: {available}") from exc


def stage_doc_abspath(root: Path, stage_id: str) -> Path:
    return root / get_stage(stage_id).doc_path
