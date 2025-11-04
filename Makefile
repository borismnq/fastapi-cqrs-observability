.PHONY: help install test run docker-up docker-down migrate clean

help:
	@echo "Available commands:"
	@echo "  make install     - Install dependencies"
	@echo "  make test        - Run tests"
	@echo "  make run         - Run application locally"
	@echo "  make docker-up   - Start Docker services"
	@echo "  make docker-down - Stop Docker services"
	@echo "  make migrate     - Run database migrations"
	@echo "  make clean       - Clean temporary files"

install:
	pip install -r requirements.txt

test:
	pytest tests/ -v --cov=app --cov-report=html

run:
	python -m uvicorn app.main:app --reload --port 8000

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down -v

migrate:
	aerich upgrade

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache htmlcov .coverage
