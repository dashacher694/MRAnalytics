import os
"""
Основной модуль приложения для MR Analytics.

Этот модуль содержит настройку FastAPI приложения,
конфигурацию и инициализацию всех необходимых компонентов, включая:
- Экземпляр приложения FastAPI
- Настройку соединения с базой данных
- Конфигурацию middleware
- Настройку маршрутов API
"""

from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse
from sqlalchemy.orm import clear_mappers
from starlette.requests import Request

from src.dependency.container import Container
from src.modules.mr_analytics.usecase.router import router
from src.core.fastapi.error import init_error_handler
from src.modules.mr_analytics.infrastructure.persistence.mapper import start_mapper
from src.core.config import settings
from src.db.connection import init_db
from src.core.logging import setup_logging

load_dotenv()

tags_metadata = [
    {"name": "MR Analytics", "description": "Анализ Merge Requests"},
]

origins = [
    "http://localhost",
    "http://localhost:3000",
]


def create_app(create_db: bool = False) -> FastAPI:
    """Create and configure FastAPI application"""
    logger = setup_logging()
    container = Container()

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        logger.info("Starting MR Analytics FastAPI Application..")

        # Initialize database
        await init_db()
        if create_db:
            # Additional database creation logic if needed
            pass

        logger.info("Start_mapper..")
        start_mapper()

        logger.info("Started MR Analytics FastAPI Application..")

        yield

        logger.info("Stopping MR Analytics FastAPI Application..")
        clear_mappers()

        logger.info("Stopped MR Analytics FastAPI Application..")

    application = FastAPI(
        title="MR Analytics API",
        version="1.0.0",
        description="GitLab Merge Requests Analytics API",
        openapi_tags=tags_metadata,
        docs_url="/docs" if settings.enable_docs else None,
        redoc_url="/redoc" if settings.enable_docs else None,
        openapi_url="/openapi.json" if settings.enable_docs else None,
        default_response_class=ORJSONResponse,
        lifespan=lifespan,
    )
    application.container = container

    # Include routers
    application.include_router(router)

    # Add middleware
    application.add_middleware(CORSMiddleware, allow_credentials=True, allow_origins=origins)
    init_error_handler(application, "admin@example.com")

    @application.middleware("http")
    async def https_proxy_middleware(request: Request, call_next):
        new_headers = dict(request.headers)
        new_headers["X-Forwarded-Proto"] = os.environ.get("FORWARDED", "http")
        request.scope["headers"] = [
            (k.lower().encode(), v.encode()) for k, v in new_headers.items()
        ]
        response = await call_next(request)
        return response

    @application.get("/health")
    async def health_check():
        return {"status": "healthy"}

    return application


app = create_app()
