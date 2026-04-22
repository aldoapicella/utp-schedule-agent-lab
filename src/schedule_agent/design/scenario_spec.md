# Scenario Spec

## Goal

The agent helps a UTP student plan a feasible semester schedule using synthetic data.

## Non-goals

- The agent must not enroll the student.
- The agent must not request UTP credentials.
- The agent must not bypass academic policy.

## Hard constraints

- No schedule conflicts.
- Respect prerequisites.
- Physical classes must match province unless fully virtual.

## Soft preferences

- Avoid Fridays.
- Prefer evening classes.
- Minimize idle time.

## Success Criteria

- The answer includes a valid schedule or a justified escalation.
- The recommendation can be reproduced with the same dataset.
