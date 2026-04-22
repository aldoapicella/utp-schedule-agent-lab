# UTP Semester Planning Scenario

## Objetivo del agente

Ayudar a un estudiante a planificar un semestre factible usando datos sintéticos.

## Entradas

- materias deseadas
- disponibilidad
- provincia
- materias obligatorias

## Salidas

- horario recomendado
- explicación
- escalamiento humano cuando aplique

```mermaid
flowchart LR
  A["Solicitud del estudiante"] --> B["Preferencias"]
  B --> C["Reglas académicas"]
  C --> D["Horario o revisión humana"]
```
