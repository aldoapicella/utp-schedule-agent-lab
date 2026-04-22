# Estructura de la Presentación

## Orden sugerido

1. `stage-00-core`
2. `stage-01-design`
3. `stage-02-tools`
4. `stage-03-orchestration`
5. memory
6. validation
7. monitoring
8. security
9. human collaboration
10. web

## Mensaje central

Primero se diseña y valida el sistema; después se expande la autonomía.

```mermaid
flowchart LR
  A["Core determinista"] --> B["Diseño"]
  B --> C["Tools tipadas"]
  C --> D["Autonomía controlada"]
```
