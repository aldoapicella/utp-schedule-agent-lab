# Facilitator Checklist

Checklist corto para ejecutar el taller en Windows, macOS o Linux sin depender de Bash ni de `make`.

## Un día antes

1. Clona el repo y cambia a `instructor-solution`.
2. Activa el entorno virtual e instala dependencias con `python -m scripts.tasks setup`.
3. Verifica prerequisitos locales con `python -m scripts.tasks doctor`.
4. Instala el frontend con `python -m scripts.tasks install-web`.
5. Carga datos sintéticos con `python -m scripts.tasks seed`.
6. Ejecuta `python -m scripts.tasks test`.
7. Ejecuta `python -m scripts.tasks stage-e2e stage-09-web`.
8. Ten preparado el branch `student-start` para los estudiantes y `instructor-solution` para demo o cierre.

## Treinta minutos antes

1. Ejecuta `python -m scripts.tasks doctor` en la máquina del facilitador.
2. Abre dos terminales:
   `python -m scripts.tasks run-api`
   `python -m scripts.tasks run-web`
3. Verifica el flujo feliz con un perfil sintético y una solicitud simple.
4. Verifica un caso de escalamiento humano con un prerrequisito faltante.
5. Ten abiertas estas referencias:
   [docs/presentation_structure.md](/home/aldo/@utp/utp-schedule-agent-lab/docs/presentation_structure.md)
   [docs/workshop_flow.md](/home/aldo/@utp/utp-schedule-agent-lab/docs/workshop_flow.md)
   [docs/stages/index.md](/home/aldo/@utp/utp-schedule-agent-lab/docs/stages/index.md)

## Durante la clase

1. Empieza con `python -m scripts.tasks doctor` para detectar problemas de entorno temprano.
2. Muestra primero `stage-00-core` para reforzar que la lógica de negocio no vive en el LLM.
3. Recorre los stages en orden y usa `python -m scripts.tasks stage-info <stage>` como guía docente.
4. Pide a los estudiantes trabajar sobre `student-start`.
5. Usa `instructor-solution` para comparar implementación, no para adelantarte al ejercicio.
6. Después de `stage-05-validation`, obliga a correr `python -m scripts.tasks eval`.
7. Después de `stage-07-security`, obliga a correr `python -m scripts.tasks attack-tests`.

## Plan de contingencia

1. Si el frontend falla en una laptop, continúa con `python -m scripts.tasks run-agent` y la API local.
2. Si `npm` no aparece en `PATH`, vuelve a correr `python -m scripts.tasks doctor` y corrige Node antes de seguir.
3. Si una máquina no logra completar el setup, usa parejas y comparte una estación funcional por equipo.
4. Si el tiempo se acorta, cubre hasta `stage-07-security` y deja `stage-08` y `stage-09` como capstone guiado.

## Cierre

1. Repite la idea central: el agente coordina, pero las reglas deterministas siguen decidiendo.
2. Pide a cada equipo mostrar:
   su resultado de `eval`
   su resultado de `attack-tests`
   una mejora para producción
3. Cierra comparando `student-start` con `instructor-solution` y los tags `stage-*`.
