# Stage 00: Core Determinista

## Pregunta guía

¿Qué parte del problema debemos resolver sin IA?

## Conceptos a explicar

- reglas de negocio vs interpretación en lenguaje natural
- datasets sintéticos y reproducibilidad
- choques de horario, provincia, virtualidad, teoría y laboratorio
- por qué el scheduler debe ser confiable antes de añadir un agente

## Ejecución

```bash
python -m scripts.tasks stage-e2e stage-00-core
```

## Actividad

Ejecutar el core, leer la salida del horario y discutir qué reglas nunca deberían dejarse al LLM.

## Señal de éxito

- el CLI genera una recomendación válida
- `tests/core` pasan
- el grupo puede nombrar al menos tres hard constraints del dominio

## Diagrama

```mermaid
flowchart LR
  A["Solicitud estructurada"] --> B["SchedulerService"]
  B --> C["Reglas de dominio"]
  C --> D["Horario válido"]
```
