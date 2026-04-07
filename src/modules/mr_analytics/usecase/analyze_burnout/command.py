from pydantic import BaseModel, Field
from typing import List, Dict, Any


class AnalyzeBurnoutRequest(BaseModel):
    team_profiles: List[Dict[str, Any]] = Field(..., description="Team reviewer profiles")


class BurnoutResponse(BaseModel):
    team_burnout_avg: float = Field(..., description="Team average burnout index")
    high_risk_reviewers: List[str] = Field(..., description="Reviewers with high burnout")
    burnout_scores: Dict[str, float] = Field(..., description="Individual burnout scores")
