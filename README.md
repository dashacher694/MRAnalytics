# MR Analytics

MR Analytics - корпоративный микросервис для анализа Merge Requests из GitLab/GitHub с продвинутыми метриками и дашбордами.

## Описание

MR Analytics - это корпоративный микросервис для сбора, анализа и визуализации данных Merge Request из систем контроля версий. Сервис предоставляет:

- Сбор и анализ Merge Requests из GitLab/GitHub
- Расчет метрик разработчиков и производительности команды
- Интерактивные дашборды для визуализации и отчетности
- API доступ для интеграции с другими системами
- Исторический анализ данных и расчет трендов
- Автоматизированная отчетность и уведомления

## Архитектура

Сервис реализован по принципам микросервисной архитектуры с использованием FastAPI. Взаимодействие с другими сервисами осуществляется через REST API. Используется асинхронный подход для высокой производительности и масштабируемости.

Основные компоненты:

- **API-интерфейс (FastAPI)** - обработка REST запросов
- **Сервисный слой** - бизнес-логика и расчет метрик
- **Инфраструктурный слой** - работа с БД (PostgreSQL/SQLAlchemy), внешние API
- **Дашборд (Streamlit)** - интерактивная визуализация
- **Конвейер данных** - автоматизированный сбор и обработка данных
- **Механизмы логирования и мониторинга** (Loguru)

## Технологический стек

- Python 3.11+
- FastAPI, Starlette
- SQLAlchemy, Alembic
- PostgreSQL
- Streamlit, Plotly
- Pandas, Scikit-learn
- Poetry (управление зависимостями)
- Loguru
- Pydantic, Pydantic-Settings
- Pytest, Coverage (тестирование)

## Интеграции

- **GitLab API** - сбор данных Merge Request
- **GitHub API** - альтернативный источник данных
- **PostgreSQL** - постоянное хранение
- **Streamlit** - визуализация дашбордов

## Безопасность

- Конфигурация через переменные окружения
- Валидация входных данных (Pydantic)
- Безопасное управление API токенами
- Разделение конфигурации и кода

## Логирование и мониторинг

- Логирование через Loguru со структурированными логами
- Метрики и отслеживание производительности
- Обработка ошибок и логирование
- Покрытие тестами через pytest-cov

## Разработка и запуск

### Предварительные требования

- Python 3.11+
- PostgreSQL
- Poetry (опционально)

### Установка

```bash
# С помощью pip
pip install -r requirements.txt

# С помощью Poetry (рекомендуется)
poetry install
```

### Конфигурация

Создать файл `.env` в корне проекта:

```bash
# Конфигурация GitLab
GITLAB_URL=https://gitlab.com
GITLAB_TOKEN=your_token_here
PROJECT_ID=12345

# Конфигурация GitHub (альтернативно)
GITHUB_TOKEN=your_github_token
GITHUB_REPO=owner/repo

# База данных
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/mr_analytics

# Приложение
LOG_LEVEL=INFO
API_HOST=0.0.0.0
API_PORT=8000
```

### Настройка базы данных

```bash
# Инициализация базы данных и выполнение миграций
make db-init

# Или вручную:
alembic upgrade head
```

### Запуск приложения

```bash
# Запуск конвейера данных (сбор данных)
make run

# Запуск дашборда
make dashboard

# Запуск API сервера
make api

# Все сервисы одновременно
python run_all.py
```

## API

### Эндпоинты

```bash
GET  /health                     # Проверка состояния
GET  /api/v1/metrics            # Все метрики
GET  /api/v1/metrics/{id}       # Метрики по ID
GET  /api/v1/merge-requests     # Все Merge Requests
GET  /api/v1/merge-requests/{id} # Merge Request по ID
POST /api/v1/collect            # Ручной сбор данных
```

### Примеры

```bash
# Проверка состояния
curl http://localhost:8000/health

# Получить все метрики
curl http://localhost:8000/api/v1/metrics

# Метрики для конкретного разработчика
curl http://localhost:8000/api/v1/metrics/123

# Запустить сбор данных вручную
curl -X POST http://localhost:8000/api/v1/collect
```

## Тестирование

### Команды тестирования

```bash
# Все тесты с покрытием
make test

# Только выполнить тесты
pytest tests/ -v

# Тесты с отчетом о покрытии
pytest tests/ --cov=src --cov-report=html

# Конкретные модули тестов
pytest tests/test_analyze_burnout.py -v
```

### Структура тестов

```bash
tests/
test_analyze_burnout.py         # Тесты анализа выгорания
test_api_endpoints.py          # Тесты API эндпоинтов
test_application_services.py   # Тесты сервисного слоя
test_integration.py            # Интеграционные тесты
```

## Качество кода

### Линтинг и форматирование

```bash
# Линтинг кода
make lint

# Форматирование кода
make format

# Оба вместе
make format && make lint
```

### Инструменты

- **Black** - форматирование кода
- **Ruff** - линтинг и форматирование
- **MyPy** - проверка типов
- **Pytest** - фреймворк тестирования

## Команды Makefile

```bash
make install              # Установить зависимости
make run                  # Запустить конвейер данных
make dashboard            # Запустить дашборд Streamlit
make api                  # Запустить сервер FastAPI
make db-init              # Инициализировать базу данных
make migrate              # Выполнить миграции
make test                 # Выполнить тесты
make lint                 # Выполнить линтинг
make format               # Отформатировать код
make clean                # Удалить сгенерированные файлы
make help                 # Показать все команды
```

## Миграции базы данных

```bash
# Создать новую миграцию
make migration-revision MSG="Add new metrics table"

# Выполнить миграции
make migrate

# Откатить последнюю миграцию
make migration-down

# Показать историю миграций
make migration-history

# Показать текущую миграцию
make migration-current
```

## Структура проекта

```bash
src/
modules/mr_analytics/          # Основной модуль
  domain/                      # Domain Layer
    aggregate/                 # Агрегаты (MR, метрики)
    services/                  # Domain Services
  infrastructure/              # Infrastructure Layer
    impl.py                    # Реализация репозитория
    uow.py                     # Unit of Work
    dto.py                     # Data Transfer Objects
  usecase/                     # Use Cases
    fetch_mrs/                 # Сбор MR
    calculate_metrics/         # Расчет метрик
persistance/                   # ORM модели
db/                           # Конфигурация БД
infrastructure/clients/        # Внешние API клиенты
core/                         # Cross-Cutting Concerns
tests/                        # Тесты
migrations/                   # Миграции базы данных
```

## Контакты

Ответственный за проект: [Ваше имя] <your.email@example.com>

## Лицензия

© 2025 MR Analytics. Все права защищены.
