from pydantic import BaseModel, Field
from typing import List, Optional


class PredictRiskRequest(BaseModel):
    days: int = Field(default=30, ge=1, le=365, description="Days to analyze")


class PredictRiskResponse(BaseModel):
    total_analyzed: int = Field(..., description="Total MRs analyzed")
    high_risk_count: int = Field(..., description="Count of high risk MRs")
    medium_risk_count: int = Field(..., description="Count of medium risk MRs")
    low_risk_count: int = Field(..., description="Count of low risk MRs")
    anomalies_count: int = Field(..., description="Count of anomalous MRs")
    risk_distribution: dict = Field(..., description="Risk score distribution")
