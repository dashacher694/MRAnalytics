from pydantic import BaseModel, Field
from typing import List, Dict, Any

from src.modules.mr_analytics.infrastructure.dto import ReviewerProfile, ReviewerSuggestion


class SuggestReviewersRequest(BaseModel):
    mr_iid: int = Field(..., description="MR IID")
    team_profiles: List[Dict[str, Any]] = Field(..., description="Team reviewer profiles")


class SuggestReviewersResponse(BaseModel):
    mr_iid: int = Field(..., description="MR IID")
    suggestions: List[ReviewerSuggestion] = Field(..., description="Reviewer suggestions")
