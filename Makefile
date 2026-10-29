.PHONY: help install fmt lint type test check run docker docker-up docker-down clean

help:
	@echo "install     Install package + dev deps with uv"
	@echo "fmt         Auto-format with ruff"
	@echo "lint        Lint with ruff (auto-fix safe rules)"
	@echo "type        Type-check with mypy"
	@echo "test        Run pytest"
	@echo "check       Run full gate (lint + format + type + test)"
	@echo "run         Run the Gradio app locally"
	@echo "docker      Build docker image"
	@echo "docker-up   Start via docker compose (needs .env)"
	@echo "docker-down Stop docker compose"
	@echo "clean       Remove caches"

install:
	uv pip install -e ".[dev]"

fmt:
	ruff format .

lint:
	ruff check --fix .

type:
	mypy

test:
	pytest

check:
	ruff check . && ruff format --check . && mypy && pytest

run:
	python postwise_ui.py

docker:
	docker build -t postwise:local -f .docker/Dockerfile .

docker-up:
	docker compose -f .docker/docker-compose.yml up --build

docker-down:
	docker compose -f .docker/docker-compose.yml down

clean:
	rm -rf .pytest_cache .ruff_cache .mypy_cache .venv
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true