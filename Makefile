PYTHON ?= python3
TASKS := $(PYTHON) -m scripts.tasks

setup:
	$(TASKS) setup

test:
	$(TASKS) test

test-core:
	$(TASKS) test-core

run-core:
	$(TASKS) run-core

seed:
	$(TASKS) seed

reset:
	$(TASKS) reset
