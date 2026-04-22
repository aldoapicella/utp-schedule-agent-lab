# UTP Schedule Agent Lab

Etapa inicial del laboratorio: un core determinista para calcular horarios UTP con datos sintéticos.

## Qué incluye este stage

- motor de horarios en [src/schedule_calculator](/home/aldo/@utp/utp-schedule-agent-lab/src/schedule_calculator)
- CLI base en [apps/cli.py](/home/aldo/@utp/utp-schedule-agent-lab/apps/cli.py)
- datasets sintéticos en [scenarios/utp_semester_planning/data](/home/aldo/@utp/utp-schedule-agent-lab/scenarios/utp_semester_planning/data)
- pruebas base en [tests/core](/home/aldo/@utp/utp-schedule-agent-lab/tests/core)

## Setup

### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m scripts.tasks init-env
python -m scripts.tasks setup
python -m scripts.tasks doctor
python -m scripts.tasks seed
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
python -m scripts.tasks test
```

## Comandos principales

```bash
python -m scripts.tasks run-core
python -m scripts.tasks test
python -m scripts.tasks reset
```

## Stages disponibles

- `stage-00-core`
- `stage-01-design`
- `stage-02-tools`
- `stage-03-orchestration`
- `stage-04-memory`
- `stage-05-validation`
- `stage-06-monitoring`
- `stage-07-security`
- `stage-08-human-collaboration`

Material:

- [docs/stages/stage-00-core.md](/home/aldo/@utp/utp-schedule-agent-lab/docs/stages/stage-00-core.md)
- [docs/stages/stage-01-design.md](/home/aldo/@utp/utp-schedule-agent-lab/docs/stages/stage-01-design.md)
- [docs/stages/stage-02-tools.md](/home/aldo/@utp/utp-schedule-agent-lab/docs/stages/stage-02-tools.md)
- [docs/stages/stage-03-orchestration.md](/home/aldo/@utp/utp-schedule-agent-lab/docs/stages/stage-03-orchestration.md)
- [docs/stages/stage-04-memory.md](/home/aldo/@utp/utp-schedule-agent-lab/docs/stages/stage-04-memory.md)
- [docs/stages/stage-05-validation.md](/home/aldo/@utp/utp-schedule-agent-lab/docs/stages/stage-05-validation.md)
- [docs/stages/stage-06-monitoring.md](/home/aldo/@utp/utp-schedule-agent-lab/docs/stages/stage-06-monitoring.md)
- [docs/stages/stage-07-security.md](/home/aldo/@utp/utp-schedule-agent-lab/docs/stages/stage-07-security.md)
- [docs/stages/stage-08-human-collaboration.md](/home/aldo/@utp/utp-schedule-agent-lab/docs/stages/stage-08-human-collaboration.md)
- [scenarios/utp_semester_planning/spec.md](/home/aldo/@utp/utp-schedule-agent-lab/scenarios/utp_semester_planning/spec.md)

Puedes inspeccionarlos con:

```bash
python -m scripts.tasks list-stages
python -m scripts.tasks stage-info stage-08-human-collaboration
python -m scripts.tasks stage-e2e stage-08-human-collaboration
```

## Compatibilidad

- Windows, macOS y Linux usan el mismo runner: `python -m scripts.tasks ...`
- `make` queda como atajo opcional en Unix
