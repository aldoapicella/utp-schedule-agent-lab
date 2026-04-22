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

run-api:
	$(TASKS) run-api

eval:
	$(TASKS) eval

trace:
	$(TASKS) trace

seed:
	$(TASKS) seed

reset:
	$(TASKS) reset
