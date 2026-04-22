# Workshop Flow

## Opening

1. Run `python -m scripts.tasks doctor`.
2. Show the scenario in [scenarios/utp_semester_planning/spec.md](/home/aldo/@utp/utp-schedule-agent-lab/scenarios/utp_semester_planning/spec.md).
3. Run `python -m scripts.tasks stage-e2e stage-00-core`.

## Guided lesson

1. Design: `python -m scripts.tasks stage-info stage-01-design`
2. Tools: `python -m scripts.tasks stage-e2e stage-02-tools`
3. Orchestration: `python -m scripts.tasks stage-e2e stage-03-orchestration`
4. Memory: `python -m scripts.tasks stage-e2e stage-04-memory`
5. Validation: `python -m scripts.tasks stage-e2e stage-05-validation`
6. Monitoring: `python -m scripts.tasks stage-e2e stage-06-monitoring`
7. Security: `python -m scripts.tasks stage-e2e stage-07-security`
8. Human collaboration: `python -m scripts.tasks stage-e2e stage-08-human-collaboration`
9. Web: `python -m scripts.tasks stage-e2e stage-09-web`

If the team is using `student-start`, keep [docs/student_todos.md](/home/aldo/@utp/utp-schedule-agent-lab/docs/student_todos.md) open during the whole session.

## Close

1. Review traces and human review tickets.
2. Compare `student-start` vs `instructor-solution` once the repo has a base commit strategy in place.
3. Ask each team what they would improve before production.
