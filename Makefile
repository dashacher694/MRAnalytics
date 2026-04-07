.PHONY: install run dashboard api test lint format clean migrate migration-revision migration-down migration-history db-init

install:
	pip install -r requirements.txt

run:
	python run_all.py

dashboard:
	streamlit run dashboard.py

api:
	uvicorn src.api.app:app --reload --host 0.0.0.0 --port 8000

# Database migration commands
migrate:
	alembic upgrade head

migration-revision:
	alembic revision --autogenerate -m "$(MSG)"

migration-down:
	alembic downgrade -1

migration-history:
	alembic history

migration-current:
	alembic current

db-init:
	mkdir -p data
	alembic upgrade head

test:
	pytest tests/ -v --cov=src

lint:
	ruff check src/
	mypy src/

format:
	black src/
	ruff check --fix src/

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
