SHELL := /bin/bash

VENV = venv

.PHONY: dev
dev: $(VENV)/pyvenv.cfg

.PHONY: run
run: $(VENV)/pyvenv.cfg  ## run AURACLE bot by default
	@. $(VENV)/bin/activate && python -u start_unified.py --bot auracle

.PHONY: run-auracle
run-auracle: $(VENV)/pyvenv.cfg  ## run AURACLE bot
	@. $(VENV)/bin/activate && python -u start_unified.py --bot auracle

.PHONY: run-solbot
run-solbot: $(VENV)/pyvenv.cfg  ## run Solana Trading Bot (Telegram)
	@. $(VENV)/bin/activate && PYTHONPATH=src/ python -u start_unified.py --bot solbot

.PHONY: test
test: $(VENV)/pyvenv.cfg  ## run test bot with test configuration
	@. $(VENV)/bin/activate && PYTHONPATH=src/ python -u src/solbot/web3/jito.py

$(VENV)/pyvenv.cfg: requirements.txt  ## create python 3 virtual environment
	python3 -m venv $(VENV)
	$(VENV)/bin/python -m pip install --upgrade pip
	$(VENV)/bin/python -m pip install -r requirements.txt
	$(VENV)/bin/python solbot_tasks.py fix-venv

.PHONY: dist
dist:
	$(VENV)/bin/python -m pip install build
	$(VENV)/bin/python -m build --sdist

.PHONY: solbot
solbot:  ## run solbot in background
	PYTHONPATH=src/ nohup python -u start_unified.py --bot solbot >> solbot.log 2>&1 &

.PHONY: auracle
auracle:  ## run AURACLE bot in background
	nohup python -u start_unified.py --bot auracle >> auracle.log 2>&1 &

kill:  ## kill running bot
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
	find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true

.PHONY: help
help:  ## show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'
