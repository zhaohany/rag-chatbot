PYTHON ?= python3

.PHONY: test

test:
	PYTHONPATH=. $(PYTHON) -m pytest -q
