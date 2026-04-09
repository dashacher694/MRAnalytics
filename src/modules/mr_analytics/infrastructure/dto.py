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
    name: str = Field(...)
    expert_files: List[str] = Field(default_factory=list)
    avg_response_time_hours: float = Field(...)
    quality_score: float = Field(...)
    open_reviews_count: int = Field(default=0)
    last_week_avg_response_time: float = Field(...)
    prev_week_avg_response_time: float = Field(...)
    last_week_avg_comment_length: int = Field(default=0)
    prev_week_avg_comment_length: int = Field(default=0)
    pending_reviews_count: int = Field(default=0)


class ReviewerSuggestion(BaseModel):
    reviewer: str = Field(...)
    score: float = Field(...)
    reasoning: str = Field(...)


class ProcessedMergeRequestDTO(BaseModel):
    iid: int = Field(...)
    title: str = Field(...)
    author: str = Field(...)
    created_at: datetime = Field(...)
    merged_at: datetime = Field(...)
    web_url: str = Field(...)
    additions: int = Field(...)
    deletions: int = Field(...)
    num_comments: int = Field(...)
    num_approvals: int = Field(...)
    total_lines_changed: int = Field(...)


class ProcessMergeRequestsResponse(BaseModel):
    processed_mrs: List[ProcessedMergeRequestDTO] = Field(...)
    total_processed: int = Field(...)
