.PHONY: help install install-dev test coverage lint format clean build docker-build docker-run

help:
	@echo "Available targets:"
	@echo "  install        - Install the package"
	@echo "  install-dev    - Install the package with development dependencies"
	@echo "  test           - Run tests"
	@echo "  coverage       - Run tests with coverage report"
	@echo "  lint           - Run linters (ruff, mypy)"
	@echo "  format         - Format code with black"
	@echo "  clean          - Clean build artifacts"
	@echo "  build          - Build distribution packages"
	@echo "  docker-build   - Build Docker image"
	@echo "  docker-run     - Run Docker container"

install:
	pip install -e .

install-dev:
	pip install -e ".[dev]"

test:
	pytest -v

coverage:
	pytest --cov=latex_server --cov-report=html --cov-report=term

lint:
	ruff check latex_server tests
	mypy latex_server

format:
	black latex_server tests

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf .pytest_cache
	rm -rf .coverage
	rm -rf htmlcov
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

build: clean
	python -m build

docker-build:
	docker build -t latex-server .

docker-run:
	docker run -p 9080:9080 latex-server