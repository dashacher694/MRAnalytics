"""
Base VCS client interface
"""
from abc import ABC, abstractmethod
from typing import List
from src.modules.mr_analytics.domain.aggregate.model import MergeRequest


class VCSClient(ABC):
    """Abstract VCS client"""
    
    @abstractmethod
    async def fetch_merge_requests(self, days: int) -> List[MergeRequest]:
        """Fetch merge requests from VCS"""
        pass
    
    @abstractmethod
    async def fetch_mr_details(self, mr_iid: int) -> dict:
        """Fetch MR details (comments, approvals, changes)"""
        pass
