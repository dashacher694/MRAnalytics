# 📊 MR Analytics

Профессиональная аналитика Merge Requests из GitLab с enterprise-архитектурой.

## Архитектура

Clean Architecture + DDD + SOLID + PostgreSQL:

```
src/
├── modules/mr_analytics/      # Модуль аналитики MR
│   ├── domain/                # Domain Layer
│   │   ├── aggregate/model.py # Aggregates (MergeRequest, MRMetrics)
│   │   └── services/          # Domain Services
│   ├── infrastructure/        # Infrastructure Layer
│   │   ├── impl.py           # Repository (ORM queries)
│   │   ├── uow.py            # Unit of Work
│   │   └── dto.py            # DTOs
│   └── usecase/              # Use Cases
│       ├── fetch_mrs/
│       │   ├── api.py        # FastAPI Controller
│       │   └── impl.py       # Use Case
│       └── calculate_metrics/
│           ├── api.py        # FastAPI Controller
│           └── impl.py       # Use Case
├── persistance/mr_metrics/    # ORM Models
│   └── entity.py             # SQLAlchemy models
├── db/                       # Database
│   ├── connection.py         # Engine, Session
│   └── transaction.py        # @transactional decorator
├── infrastructure/clients/    # External clients
│   ├── base.py              # VCSClient Protocol
│   └── gitlab.py            # GitLab API
└── core/                     # Cross-cutting
    ├── config.py            # Pydantic Settings
    ├── containers.py        # DI Container
    ├── errors.py            # Exceptions
    └── logging.py           # Loguru
```

## Паттерны

- ✅ **Repository Pattern** (Protocol + SQLAlchemy ORM)
- ✅ **Unit of Work** (транзакции)
- ✅ **Dependency Injection** (dependency-injector)
- ✅ **Use Case Pattern** (папка на use case)
- ✅ **Domain Services** (бизнес-логика)
- ✅ **API Controllers** (FastAPI в usecase/*/api.py)
- ✅ **ORM** (SQLAlchemy async + PostgreSQL)
- ✅ **Transaction Decorator** (@transactional)
- ✅ **SOLID** (все принципы)

## Установка

```bash
pip install -r requirements.txt
```

## Конфигурация

`.env`:
```bash
GITLAB_TOKEN=your_token
GITLAB_URL=https://gitlab.com
PROJECT_ID=12345
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/mr_analytics
```

## Запуск

```bash
# Pipeline
python run_all.py

# Dashboard
streamlit run dashboard.py

# API
uvicorn src.modules.mr_analytics.usecase.calculate_metrics.api:app --reload
```

## API

```
GET /health              # Health check
GET /api/v1/metrics      # All metrics
GET /api/v1/metrics/{id} # By IID
```

## Makefile

```bash
make run       # Pipeline
make dashboard # Dashboard
make api       # API server
```
