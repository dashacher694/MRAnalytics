from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field


class GetMetricsRequest(BaseModel):
    mr_iid: Optional[int] = Field(default=None, description="Filter by MR IID")
    author: Optional[str] = Field(default=None, description="Filter by author")
    days: int = Field(default=30, ge=1, le=365, description="Filter by last N days")


class GetMetricsResponse(BaseModel):
    metrics: List[dict] = Field(..., description="List of MR metrics")
    total: int = Field(..., description="Total count")
