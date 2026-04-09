from dataclasses import dataclass
from typing import List
from src.modules.mr_analytics.infrastructure.dto import VCSMergeRequestData


@dataclass
class FetchMergeRequestsCommand:
    days: int = 30


@dataclass
class FetchMergeRequestsResponse:
    mrs: List[VCSMergeRequestData]
    total_fetched: int
