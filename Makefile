.PHONY: install run dashboard api test lint format clean migrate migration-revision migration-down migration-history db-init

install:
	poetry install

run:
	poetry run python run_all.py

dashboard:
	poetry run streamlit run dashboard.py

api:
	poetry run uvicorn src.api.app:app --reload --host 0.0.0.0 --port 8000

# Database migration commands
migrate:
	poetry run alembic upgrade head

migration-revision:
	poetry run alembic revision --autogenerate -m "$(MSG)"

migration-down:
	poetry run alembic downgrade -1

migration-history:
	poetry run alembic history

migration-current:
	poetry run alembic current

db-init:
	mkdir -p data
	poetry run alembic upgrade head

test:
	poetry run pytest tests/ -v --cov=src

lint:
	poetry run ruff check src/
	poetry run mypy src/

format:
	poetry run black src/
	poetry run ruff check --fix src/

clean:
	rm -rf data/*.db
	rm -rf logs/*.log
	rm -rf __pycache__
	rm -rf src/**/__pycache__
	rm -rf .pytest_cache
	rm -rf .mypy_cache
	rm -rf .ruff_cache

help:
	@echo "Available commands:"
	@echo "  make install           - Install dependencies"
	@echo "  make run               - Run data collection pipeline"
	@echo "  make dashboard         - Start Streamlit dashboard"
	@echo "  make api               - Start FastAPI server"
	@echo "  make db-init           - Initialize database and run migrations"
	@echo "  make migrate           - Run database migrations"
	@echo "  make migration-revision MSG='message' - Create new migration"
	@echo "  make migration-down    - Rollback last migration"
	@echo "  make migration-history - Show migration history"
	@echo "  make migration-current - Show current migration"
	@echo "  make test              - Run tests with coverage"
	@echo "  make lint              - Run linters"
	@echo "  make format            - Format code"
	@echo "  make clean             - Clean generated files"
