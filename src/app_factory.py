"""
Application factory and configuration
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI

from src.modules.mr_analytics.usecase.router import router
from src.core.fastapi.error import init_error_handler
from src.modules.mr_analytics.infrastructure.persistence.mapper import start_mapper


@asynccontextmanager
async def lifespan(app: FastAPI):
    start_mapper()
    yield


def create_app() -> FastAPI:
    """Create and configure FastAPI application"""
    app = FastAPI(
        title="MR Analytics API",
        description="GitLab Merge Requests Analytics API",
        version="1.0.0",
        lifespan=lifespan
    )
    
    init_error_handler(app, "admin@example.com")
    app.include_router(router)
    
    @app.get("/health")
    async def health_check():
        return {"status": "healthy"}
    
    return app
