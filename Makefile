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

run-agent:
	$(TASKS) run-agent

eval:
	$(TASKS) eval

seed:
	$(TASKS) seed

reset:
	$(TASKS) reset
