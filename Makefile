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

install-web:
	$(TASKS) install-web

run-web:
	$(TASKS) run-web

run-ui:
	$(TASKS) run-ui

eval:
	$(TASKS) eval

attack-tests:
	$(TASKS) attack-tests

trace:
	$(TASKS) trace

seed:
	$(TASKS) seed

reset:
	$(TASKS) reset
