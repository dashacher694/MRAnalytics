from fastapi import FastAPI

from src.modules.mr_analytics.usecase.get_metrics import api as get_metrics_api
from src.modules.mr_analytics.usecase.fetch_mrs import api as fetch_mrs_api
from src.modules.mr_analytics.usecase.process_mrs import api as process_mrs_api
from src.modules.mr_analytics.usecase.run_analysis import api as run_analysis_api


def add_routes(app: FastAPI):
    """Add all API routes to the FastAPI application"""
    # Import and register all API endpoints
    app.include_router(get_metrics_api.router)
    app.include_router(fetch_mrs_api.router)
    app.include_router(process_mrs_api.router)
    app.include_router(run_analysis_api.router)
