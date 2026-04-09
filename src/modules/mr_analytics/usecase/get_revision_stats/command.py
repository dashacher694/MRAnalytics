from dataclasses import dataclass
from typing import Optional


@dataclass
class GetRevisionStatsRequest:
    """Request for revision statistics"""
    days: int = 30
    author: Optional[str] = None


@dataclass
class GetRevisionStatsResponse:
    """Response with revision statistics"""
    total_mrs: int
    mrs_with_changes_requested: int
    mrs_without_changes_requested: int
    changes_requested_rate: float
    total_changes_requested: int
    avg_changes_per_mr: float
    author_stats: dict
