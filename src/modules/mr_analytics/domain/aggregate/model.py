from dataclasses import dataclass, field
from datetime import datetime
from typing import List

from src.modules.mr_analytics.domain.value_objects import Comment, Approval
from src.modules.mr_analytics.domain.enums import RiskScore


@dataclass
class MergeRequest:
    iid: int = 0
    title: str = ""
    author: str = ""
    created_at: datetime | None = None
    merged_at: datetime | None = None
    web_url: str = ""
    additions: int = 0
    deletions: int = 0
    comments: List[Comment] = field(default_factory=list)
    approvals: List[Approval] = field(default_factory=list)
    changed_files: List[str] = field(default_factory=list)
    author_mr_count: int = 0
    creation_hour: int = 0
    is_critical_files: bool = False
    unique_reviewers: List[str] = field(default_factory=list)
    risk_score: RiskScore = RiskScore.LOW


@dataclass
class MRMetrics:
    mr_iid: int = 0
    title: str = ""
    author: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    merged_at: datetime = field(default_factory=datetime.now)
    web_url: str = ""
    additions: int = 0
    deletions: int = 0
    time_to_merge: float | None = None
    review_rounds: int = 0
    comment_density: float = 0.0
    formal_approval: int = 0
    response_time_hours: float | None = None
    num_comments: int = 0
    num_approvals: int = 0
    changes_requested: int = 0
    risk_score: RiskScore = RiskScore.LOW
    suggested_reviewers: List[str] = field(default_factory=list)
    reviewer_burnout_index: float = 0.0
    is_anomaly: bool = False
