SHELL := /bin/bash

VENV = venv

.PHONY: dev
dev: $(VENV)/pyvenv.cfg

.PHONY: run
run: $(VENV)/pyvenv.cfg  ## run AURACLE bot by default (local mode)
	@. $(VENV)/bin/activate && python -u start_local.py --bot auracle

.PHONY: run-auracle
run-auracle: $(VENV)/pyvenv.cfg  ## run AURACLE bot (local mode)
	@. $(VENV)/bin/activate && python -u start_local.py --bot auracle

.PHONY: run-solbot
run-solbot: $(VENV)/pyvenv.cfg  ## run Solana Trading Bot (Telegram, local mode)
	@. $(VENV)/bin/activate && python -u start_local.py --bot solbot

.PHONY: test
test: $(VENV)/pyvenv.cfg  ## run demo test (local mode)
	@. $(VENV)/bin/activate && python -u start_local.py --test

.PHONY: setup
setup: $(VENV)/pyvenv.cfg  ## run local setup wizard
	@. $(VENV)/bin/activate && python -u start_local.py --setup

# Original unified startup (still supported)
.PHONY: run-unified
run-unified: $(VENV)/pyvenv.cfg  ## run with original unified startup
	@. $(VENV)/bin/activate && python -u start_unified.py --bot auracle

$(VENV)/pyvenv.cfg: requirements.local.txt  ## create python 3 virtual environment (local deps)
	python3 -m venv $(VENV)
	$(VENV)/bin/python -m pip install --upgrade pip
	$(VENV)/bin/python -m pip install -r requirements.local.txt
	@echo "✅ Local development environment ready"

.PHONY: install
install:  ## install dependencies without virtual environment
	python -m pip install --upgrade pip
	python -m pip install -r requirements.local.txt

.PHONY: dist
dist:
	$(VENV)/bin/python -m pip install build
	$(VENV)/bin/python -m build --sdist

.PHONY: solbot
solbot:  ## run solbot in background (local mode)
	nohup python -u start_local.py --bot solbot >> solbot.log 2>&1 &

.PHONY: auracle
auracle:  ## run AURACLE bot in background (local mode)
	nohup python -u start_local.py --bot auracle >> auracle.log 2>&1 &

kill:  ## kill running bot
	pkill -U $$USER -f "start_local.py"
	pkill -U $$USER -f "start_unified.py"
	pkill -U $$USER -f "src/solbot/main.py"
	pkill -U $$USER -f "make run"

.PHONY: clean
clean:  ## clean up logs and temporary files
	rm -f *.log
	rm -rf $(VENV)
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf data/logs/*
	find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true

.PHONY: help
help:  ## show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'
