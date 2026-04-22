# UTP Schedule Agent Lab

Monorepo para un laboratorio de Agent Engineering aplicado a planificación de horarios UTP. El proyecto combina:

- un core determinista de cálculo de horarios en `src/schedule_calculator`
- una capa agentic en `src/schedule_agent`
- una API en FastAPI en `apps/api`
- un frontend web en Next.js en `apps/web`

## Qué resuelve

El agente recibe una solicitud de un estudiante con materias deseadas, restricciones horarias, provincia y preferencias. Luego:

1. extrae preferencias seguras
2. consulta perfil y catálogo sintético
3. valida prerrequisitos
4. calcula el mejor horario con reglas deterministas
5. valida el resultado
6. explica la recomendación o escala a revisión humana

El laboratorio no usa scraping vivo ni credenciales reales.

## Estructura

```text
apps/
  api/         FastAPI
  web/         Next.js
src/
  schedule_calculator/
  schedule_agent/
scenarios/
tests/
scripts/
```

## Setup

### Requisitos

- Python 3.10+ y `venv`
- Node.js 20+ con `npm`
- Git

El flujo oficial del taller es multiplataforma y no depende de `make`. Todas las tareas principales pueden ejecutarse con `python -m scripts.tasks ...` en Windows, macOS y Linux.

### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m scripts.tasks init-env
python -m scripts.tasks setup
python -m scripts.tasks doctor
python -m scripts.tasks seed
python -m scripts.tasks install-web
python -m scripts.tasks test
```

### Windows PowerShell

```powershell
py -3.12 -m venv .venv
.venv\Scripts\Activate.ps1
python -m scripts.tasks init-env
python -m scripts.tasks setup
python -m scripts.tasks doctor
python -m scripts.tasks seed
python -m scripts.tasks install-web
python -m scripts.tasks test
```

## Comandos principales

```bash
python -m scripts.tasks run-core
python -m scripts.tasks run-agent
python -m scripts.tasks run-api
python -m scripts.tasks run-web
python -m scripts.tasks eval
python -m scripts.tasks attack-tests
python -m scripts.tasks reset
```

## Flujo del workshop

```bash
python -m scripts.tasks run-ui
```

Ese comando imprime las instrucciones para abrir la API y el frontend en dos terminales. Si prefieres, también puedes levantar ambos procesos manualmente:

```bash
python -m scripts.tasks run-api
python -m scripts.tasks run-web
```

## Estructura didáctica

El taller está organizado en stages incrementales. Puedes explorar el material con:

```bash
python -m scripts.tasks list-stages
python -m scripts.tasks stage-info stage-05-validation
python -m scripts.tasks stage-e2e stage-07-security
```

Material recomendado:

- [docs/presentation_structure.md](/home/aldo/@utp/utp-schedule-agent-lab/docs/presentation_structure.md)
- [docs/stages/index.md](/home/aldo/@utp/utp-schedule-agent-lab/docs/stages/index.md)
- [scenarios/utp_semester_planning/spec.md](/home/aldo/@utp/utp-schedule-agent-lab/scenarios/utp_semester_planning/spec.md)
- [docs/facilitator_checklist.md](/home/aldo/@utp/utp-schedule-agent-lab/docs/facilitator_checklist.md)

## Release del taller

La release pública recomendada para facilitación es `v1.0.0-workshop`. Sus notas viven en:

- [docs/releases/v1.0.0-workshop.md](/home/aldo/@utp/utp-schedule-agent-lab/docs/releases/v1.0.0-workshop.md)

## Compatibilidad

- Windows: usa PowerShell y el runner `python -m scripts.tasks`.
- macOS: usa Terminal o iTerm con el mismo runner.
- Linux: usa Bash, Zsh o cualquier shell, también con el mismo runner.
- `make` se mantiene como atajo opcional para macOS y Linux, pero no es necesario para el taller.

## Comandos opcionales con make

```bash
make setup
make test
make run-api
make run-web
make eval
```

## Frontend

La web está en `apps/web` y consume únicamente la API del backend. Usa un dashboard único con cuatro paneles:

- chat del estudiante
- recomendación y explicación
- timeline de tool calls
- memoria, validación y revisión humana

## Etapas del laboratorio

- `stage-00-core`
- `stage-01-design`
- `stage-02-tools`
- `stage-03-orchestration`
- `stage-04-memory`
- `stage-05-validation`
- `stage-06-monitoring`
- `stage-07-security`
- `stage-08-human-collaboration`
- `stage-09-web`
