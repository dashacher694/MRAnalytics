"""
Common DTO models for VCS data and analytics
"""
from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field


class CommentData(BaseModel):
    author: str = Field(default="")
    created_at: Optional[str] = Field(default=None)
    body: str = Field(default="")
    resolvable: bool = Field(default=False)


class ApprovalData(BaseModel):
    approver: str = Field(default="")
    approved_at: Optional[str] = Field(default=None)


class VCSMergeRequestData(BaseModel):
    iid: int = Field(default=0)
    title: str = Field(default="")
    author: str = Field(default="")
    created_at: Optional[str] = Field(default=None)
    merged_at: Optional[str] = Field(default=None)
    web_url: str = Field(default="")
    additions: int = Field(default=0)
    deletions: int = Field(default=0)
    comments: List[CommentData] = Field(default_factory=list)
    approvals: List[ApprovalData] = Field(default_factory=list)


class ReviewerProfile(BaseModel):
    name: str = Field(..., description="Reviewer name")
    expert_files: List[str] = Field(default_factory=list, description="Files reviewer is expert in")
    avg_response_time_hours: float = Field(..., description="Average response time in hours")
    quality_score: float = Field(..., description="Quality score (0-1)")
    open_reviews_count: int = Field(default=0, description="Currently open reviews")
    last_week_avg_response_time: float = Field(..., description="Last week avg response time")
    prev_week_avg_response_time: float = Field(..., description="Previous week avg response time")
    last_week_avg_comment_length: int = Field(default=0, description="Last week avg comment length")
    prev_week_avg_comment_length: int = Field(default=0, description="Previous week avg comment length")
    pending_reviews_count: int = Field(default=0, description="Pending reviews count")


class ReviewerSuggestion(BaseModel):
    reviewer: str = Field(..., description="Reviewer name")
    score: float = Field(..., description="Compatibility score")
    reasoning: str = Field(..., description="Reasoning for suggestion")


class ProcessedMergeRequestDTO(BaseModel):
    iid: int = Field(..., description="IID Merge Request")
    title: str = Field(..., description="Title MR")
    author: str = Field(..., description="Author MR")
    created_at: datetime = Field(..., description="Date creation MR")
    merged_at: datetime = Field(..., description="Date merge MR")
    web_url: str = Field(..., description="URL MR")
    additions: int = Field(..., description="Lines added")
    deletions: int = Field(..., description="Lines deleted")
    num_comments: int = Field(..., description="Count comments")
    num_approvals: int = Field(..., description="Count approvals")
    total_lines_changed: int = Field(..., description="Total lines changed")


class ProcessMergeRequestsResponse(BaseModel):
    processed_mrs: List[ProcessedMergeRequestDTO] = Field(..., description="List of processed MRs")
    total_processed: int = Field(..., description="Total count processed")
