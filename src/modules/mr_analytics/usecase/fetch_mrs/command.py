"""
Commands for fetching merge requests from VCS
"""
from dataclasses import dataclass
from typing import List
from src.modules.mr_analytics.infrastructure.dto import VCSMergeRequestData


@dataclass
class FetchMergeRequestsCommand:
    """Command to fetch merge requests from VCS"""
    days: int = 30


@dataclass
class FetchMergeRequestsResponse:
    """Response with fetched merge requests"""
    mrs: List[VCSMergeRequestData]
    total_fetched: int
