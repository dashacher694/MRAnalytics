from fastapi import APIRouter

from .get_metrics import router as metrics_router
from .predict_risk import router as risk_router
from .suggest_reviewers import router as reviewers_router
from .analyze_burnout import router as burnout_router

router = APIRouter(prefix="/api/v1", tags=["MR Analytics"])

router.include_router(metrics_router, prefix="/metrics", tags=["Metrics"])
router.include_router(risk_router, prefix="/risk", tags=["Risk Prediction"])
router.include_router(reviewers_router, prefix="/reviewers", tags=["Reviewers"])
router.include_router(burnout_router, prefix="/burnout", tags=["Burnout Analysis"])
