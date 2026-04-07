from datetime import datetime
from typing import List
from pydantic import BaseModel, Field, ConfigDict


class MRMetricsResponse(BaseModel):
    
    model_config = ConfigDict(from_attributes=True)
    
    mr_iid: int = Field(..., description="IID Merge Request", alias="mrIid")
    title: str = Field(..., description="Title MR")
    author: str = Field(..., description="Author MR")
    created_at: datetime = Field(..., description="Date creation MR", alias="createdAt")
    merged_at: datetime = Field(..., description="Date merge MR", alias="mergedAt")
    web_url: str = Field(..., description="URL MR", alias="webUrl")
    additions: int = Field(..., description="Lines added")
    deletions: int = Field(..., description="Lines deleted")
    time_to_merge: float | None = Field(None, description="Time to merge (hours)", alias="timeToMerge")
    review_rounds: int = Field(..., description="Count review rounds", alias="reviewRounds")
    comment_density: float = Field(..., description="Comments per line of code", alias="commentDensity")
    formal_approval: int = Field(..., description="Flag formal approval (0/1)", alias="formalApproval")
    response_time_hours: float | None = Field(None, description="Response time (hours)", alias="responseTimeHours")
    num_comments: int = Field(..., description="Count comments", alias="numComments")
    num_approvals: int = Field(..., description="Count approvals", alias="numApprovals")


class MRMetricsListResponse(BaseModel):
    
    data: List[MRMetricsResponse] = Field(..., description="List metrics")
    total: int = Field(..., description="Total count metrics")


class MRMetricsDTO(BaseModel):
    """DTO for MRMetrics"""
    mr_iid: int = Field(..., description="MR IID")
    title: str = Field(..., description="Title")
    author: str = Field(..., description="Author")
    created_at: datetime = Field(..., description="Created at")
    merged_at: datetime = Field(..., description="Merged at")
    web_url: str = Field(..., description="Web URL")
    additions: int = Field(..., description="Additions")
    deletions: int = Field(..., description="Deletions")
    time_to_merge: float | None = Field(None, description="Time to merge")
    review_rounds: int = Field(..., description="Review rounds")
    comment_density: float = Field(..., description="Comment density")
    formal_approval: int = Field(..., description="Formal approval")
    response_time_hours: float | None = Field(None, description="Response time")
    num_comments: int = Field(..., description="Number of comments")
    num_approvals: int = Field(..., description="Number of approvals")


class MRAnalyticsSummaryDTO(BaseModel):
    """DTO for MR analytics summary"""
    total_mrs: int = Field(..., description="Total MRs")
    avg_time_to_merge: float = Field(..., description="Average time to merge")
    avg_review_rounds: float = Field(..., description="Average review rounds")
    total_comments: int = Field(..., description="Total comments")
    total_approvals: int = Field(..., description="Total approvals")


class AuthorStatsDTO(BaseModel):
    """DTO for author statistics"""
    author: str = Field(..., description="Author name")
    mr_count: int = Field(..., description="Number of MRs")
    avg_time_to_merge: float = Field(..., description="Average time to merge")
    total_additions: int = Field(..., description="Total additions")
    total_deletions: int = Field(..., description="Total deletions")


class ErrorResponse(BaseModel):
    
    detail: str = Field(..., description="Error message")
