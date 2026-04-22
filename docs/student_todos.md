# Student TODO Map

Esta rama está pensada para clase. El sistema sigue corriendo, pero el trabajo del estudiante es recorrerlo por etapas, entenderlo y completar o defender decisiones de implementación usando los archivos indicados.

## Cómo usar esta rama

1. Corre `python -m scripts.tasks doctor`
2. Corre `python -m scripts.tasks list-stages`
3. Usa el stage actual de la clase como punto de entrada
4. Documenta tu respuesta o cambio antes de editar código

## Stage 00: Core

Archivos foco:

- [src/schedule_calculator/application/scheduler.py](/home/aldo/@utp/utp-schedule-agent-lab/src/schedule_calculator/application/scheduler.py)
- [src/schedule_calculator/domain/rules.py](/home/aldo/@utp/utp-schedule-agent-lab/src/schedule_calculator/domain/rules.py)
- [tests/core/test_scheduler_service.py](/home/aldo/@utp/utp-schedule-agent-lab/tests/core/test_scheduler_service.py)

TODOs:

- Explica qué reglas nunca deberían resolverse solo con LLM.
- Identifica qué constraints son duras y cuáles optimizan la experiencia.
- Ejecuta `python -m scripts.tasks stage-e2e stage-00-core`.

## Stage 01: Design

Archivos foco:

- [src/schedule_agent/design/scenario_spec.md](/home/aldo/@utp/utp-schedule-agent-lab/src/schedule_agent/design/scenario_spec.md)
- [src/schedule_agent/design/constraints.md](/home/aldo/@utp/utp-schedule-agent-lab/src/schedule_agent/design/constraints.md)
- [src/schedule_agent/design/architecture.md](/home/aldo/@utp/utp-schedule-agent-lab/src/schedule_agent/design/architecture.md)

TODOs:

- Agrega una restricción faltante en `scenario_spec.md`.
- Justifica si pertenece a hard constraint, soft preference o non-goal.
- Ejecuta `python -m scripts.tasks stage-test stage-01-design`.

## Stage 02: Tools

Archivos foco:

- [src/schedule_agent/tools/catalog_tools.py](/home/aldo/@utp/utp-schedule-agent-lab/src/schedule_agent/tools/catalog_tools.py)
- [src/schedule_agent/tools/schedule_tools.py](/home/aldo/@utp/utp-schedule-agent-lab/src/schedule_agent/tools/schedule_tools.py)
- [src/schedule_agent/tools/schemas.py](/home/aldo/@utp/utp-schedule-agent-lab/src/schedule_agent/tools/schemas.py)

TODOs:

- Recorre `check_prerequisites()` y explica su contrato.
- Recorre `calculate_best_schedule()` y explica su input/output.
- Ejecuta `python -m scripts.tasks stage-e2e stage-02-tools`.

## Stage 03: Orchestration

Archivos foco:

- [src/schedule_agent/orchestration/state.py](/home/aldo/@utp/utp-schedule-agent-lab/src/schedule_agent/orchestration/state.py)
- [src/schedule_agent/orchestration/planner_executor.py](/home/aldo/@utp/utp-schedule-agent-lab/src/schedule_agent/orchestration/planner_executor.py)
- [src/schedule_agent/orchestration/simple_agent.py](/home/aldo/@utp/utp-schedule-agent-lab/src/schedule_agent/orchestration/simple_agent.py)

TODOs:

- Dibuja el flujo `extract -> check -> calculate -> validate -> respond`.
- Señala dónde se decide escalar a humano.
- Ejecuta `python -m scripts.tasks stage-e2e stage-03-orchestration`.

## Stage 04: Memory

Archivos foco:

- [src/schedule_agent/memory/preference_extractor.py](/home/aldo/@utp/utp-schedule-agent-lab/src/schedule_agent/memory/preference_extractor.py)
- [src/schedule_agent/memory/session_memory.py](/home/aldo/@utp/utp-schedule-agent-lab/src/schedule_agent/memory/session_memory.py)

TODOs:

- Identifica qué preferencias se guardan y por qué.
- Identifica qué datos nunca se deben persistir.
- Ejecuta `python -m scripts.tasks stage-e2e stage-04-memory`.

## Stage 05: Validation

Archivos foco:

- [src/schedule_agent/validation/evaluator.py](/home/aldo/@utp/utp-schedule-agent-lab/src/schedule_agent/validation/evaluator.py)
- [src/schedule_agent/validation/metrics.py](/home/aldo/@utp/utp-schedule-agent-lab/src/schedule_agent/validation/metrics.py)
- [src/schedule_agent/validation/datasets/eval_set.jsonl](/home/aldo/@utp/utp-schedule-agent-lab/src/schedule_agent/validation/datasets/eval_set.jsonl)

TODOs:

- Explica cada métrica del summary de evaluación.
- Propón una métrica adicional para producción.
- Ejecuta `python -m scripts.tasks stage-e2e stage-05-validation`.

## Stage 06: Monitoring

Archivos foco:

- [src/schedule_agent/monitoring/telemetry.py](/home/aldo/@utp/utp-schedule-agent-lab/src/schedule_agent/monitoring/telemetry.py)
- [src/schedule_agent/monitoring/structured_logger.py](/home/aldo/@utp/utp-schedule-agent-lab/src/schedule_agent/monitoring/structured_logger.py)
- [src/schedule_agent/monitoring/trace_viewer.py](/home/aldo/@utp/utp-schedule-agent-lab/src/schedule_agent/monitoring/trace_viewer.py)

TODOs:

- Sigue una ejecución real hasta `agent.completed`.
- Identifica una latencia y un resultado de tool call.
- Ejecuta `python -m scripts.tasks stage-e2e stage-06-monitoring`.

## Stage 07: Security

Archivos foco:

- [src/schedule_agent/security/input_guard.py](/home/aldo/@utp/utp-schedule-agent-lab/src/schedule_agent/security/input_guard.py)
- [src/schedule_agent/security/pii_redaction.py](/home/aldo/@utp/utp-schedule-agent-lab/src/schedule_agent/security/pii_redaction.py)
- [src/schedule_agent/security/tool_permissions.py](/home/aldo/@utp/utp-schedule-agent-lab/src/schedule_agent/security/tool_permissions.py)

TODOs:

- Clasifica cada ataque del dataset adversarial.
- Explica qué defensa lo detiene.
- Ejecuta `python -m scripts.tasks stage-e2e stage-07-security`.

## Stage 08: Human Collaboration

Archivos foco:

- [src/schedule_agent/human/escalation_policy.py](/home/aldo/@utp/utp-schedule-agent-lab/src/schedule_agent/human/escalation_policy.py)
- [src/schedule_agent/human/approval_queue.py](/home/aldo/@utp/utp-schedule-agent-lab/src/schedule_agent/human/approval_queue.py)
- [src/schedule_agent/human/advisor_console.py](/home/aldo/@utp/utp-schedule-agent-lab/src/schedule_agent/human/advisor_console.py)

TODOs:

- Describe cuándo el agente debe detenerse.
- Fuerza un caso con prerrequisito faltante y revisa el ticket.
- Ejecuta `python -m scripts.tasks stage-e2e stage-08-human-collaboration`.

## Stage 09: Web

Archivos foco:

- [apps/api/main.py](/home/aldo/@utp/utp-schedule-agent-lab/apps/api/main.py)
- [apps/web/components/dashboard.tsx](/home/aldo/@utp/utp-schedule-agent-lab/apps/web/components/dashboard.tsx)
- [apps/web/components/weekly-schedule.tsx](/home/aldo/@utp/utp-schedule-agent-lab/apps/web/components/weekly-schedule.tsx)

TODOs:

- Explica qué panel de la UI representa cada dimensión del sistema agentic.
- Recorre un caso feliz y un caso con revisión humana.
- Ejecuta `python -m scripts.tasks stage-e2e stage-09-web`.
