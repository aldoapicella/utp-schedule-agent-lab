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

## Stage actual

- `stage-00-core`
- guía de clase: [docs/stages/stage-00-core.md](/home/aldo/@utp/utp-schedule-agent-lab/docs/stages/stage-00-core.md)

## Compatibilidad

- Windows, macOS y Linux usan el mismo runner: `python -m scripts.tasks ...`
- `make` queda como atajo opcional en Unix
