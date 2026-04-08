"""Use cases"""

from fastapi import APIRouter

router = APIRouter(
    prefix="/api/v1/mr-analytics",
    tags=["MR Analytics"],
)

# Import API modules to register endpoints
from src.modules.mr_analytics.usecase.get_metrics import api
