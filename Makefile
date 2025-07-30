SHELL := /bin/bash

VENV = venv

.PHONY: dev
dev: $(VENV)/pyvenv.cfg

.PHONY: run
run: $(VENV)/pyvenv.cfg  ## run AURACLE Forex bot (default)
	@. $(VENV)/bin/activate && python -u start_forex.py

.PHONY: run-forex
run-forex: $(VENV)/pyvenv.cfg  ## run AURACLE Forex bot
	@. $(VENV)/bin/activate && python -u start_forex.py

.PHONY: run-dashboard
run-dashboard: $(VENV)/pyvenv.cfg  ## run AURACLE with web dashboard
	@. $(VENV)/bin/activate && python -u dashboard/app.py

.PHONY: test
test: $(VENV)/pyvenv.cfg  ## run tests
	@. $(VENV)/bin/activate && python -m pytest tests/ -v

.PHONY: backtest
backtest: $(VENV)/pyvenv.cfg  ## run strategy backtesting
	@. $(VENV)/bin/activate && python -c "from backtest_engine import BacktestEngine; print('Run backtesting with: python backtest_example.py')"

.PHONY: setup
setup: $(VENV)/pyvenv.cfg  ## run setup wizard
	@. $(VENV)/bin/activate && python -u setup_local.py

$(VENV)/pyvenv.cfg: requirements.txt  ## create python 3 virtual environment
	python3 -m venv $(VENV)
	$(VENV)/bin/python -m pip install --upgrade pip
	$(VENV)/bin/python -m pip install -r requirements.txt
	@echo "✅ Forex trading environment ready"

.PHONY: install
install:  ## install dependencies without virtual environment
	python -m pip install --upgrade pip
	python -m pip install -r requirements.txt

.PHONY: dist
dist:
	$(VENV)/bin/python -m pip install build
	$(VENV)/bin/python -m build --sdist

.PHONY: forex
forex:  ## run AURACLE Forex bot in background
	nohup python -u start_forex.py >> auracle-forex.log 2>&1 &

.PHONY: dashboard
dashboard:  ## run dashboard in background
	nohup python -u dashboard/app.py >> dashboard.log 2>&1 &

.PHONY: docker-build
docker-build:  ## build Docker image
	docker build -t auracle-forex:latest .

.PHONY: docker-run
docker-run:  ## run Docker container
	docker-compose up -d

.PHONY: docker-stop
docker-stop:  ## stop Docker containers
	docker-compose down

.PHONY: docker-logs
docker-logs:  ## show Docker logs
	docker-compose logs -f

kill:  ## kill running processes
	pkill -U $$USER -f "start_forex.py"
	pkill -U $$USER -f "dashboard/app.py"
	pkill -U $$USER -f "make run"

.PHONY: clean
clean:  ## clean up logs and temporary files
	rm -f *.log
	rm -rf $(VENV)
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf data/logs/*
	rm -rf data/backtests/*.png
	rm -rf data/backtests/*.html
	find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true

.PHONY: lint
lint: $(VENV)/pyvenv.cfg  ## run code linting
	@. $(VENV)/bin/activate && python -m flake8 --max-line-length=120 --ignore=E501,W503 *.py strategies/ dashboard/

.PHONY: format
format: $(VENV)/pyvenv.cfg  ## format code with black
	@. $(VENV)/bin/activate && python -m black --line-length=120 *.py strategies/ dashboard/

.PHONY: check-strategies
check-strategies: $(VENV)/pyvenv.cfg  ## validate strategy files
	@. $(VENV)/bin/activate && python -c "from strategies.strategy_loader import StrategyLoader; loader = StrategyLoader(); loader.load_all_strategies(); print('All strategies loaded successfully')"

.PHONY: help
help:  ## show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'
