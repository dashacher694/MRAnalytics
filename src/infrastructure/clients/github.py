"""
GitHub API client implementation
"""
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Any
from loguru import logger

from src.modules.mr_analytics.domain.aggregate.model import MergeRequest
from src.modules.mr_analytics.domain.value_objects import Comment
from src.infrastructure.clients.base import VCSClient
from src.core.errors import APIError


class GitHubClient(VCSClient):
    """GitHub API client"""
    
    def __init__(self, token: str, repo: str, timeout: int = 30):
        self.token = token
        self.repo = repo
        self.timeout = timeout
        self.base_url = "https://api.github.com"
        self.headers = {
            'Authorization': f'Bearer {token}',
            'Accept': 'application/vnd.github.v3+json'
        }
    
    async def fetch_merge_requests(self, state: str = "closed", created_after: datetime = None, created_before: datetime = None) -> List[dict]:
        """Fetch PRs from GitHub as raw dict data"""
        params = {
            'state': state,
            'per_page': 100,
            'page': 1,
            'sort': 'created',
            'direction': 'desc'
        }
        
        if created_after:
            params['since'] = created_after.isoformat()
        if created_before:
            params['until'] = created_before.isoformat()
        
        url = f"{self.base_url}/repos/{self.repo}/pulls"
        
        try:
            logger.info(f"Fetching PRs from GitHub: {self.repo}")
            response = requests.get(url, headers=self.headers, params=params, timeout=self.timeout)
            response.raise_for_status()
            
            prs = response.json()
            logger.success(f"Fetched {len(prs)} PRs from GitHub")
            return prs
            
        except requests.exceptions.RequestException as e:
            logger.error(f"GitHub API error: {e}")
            raise APIError(f"GitHub API error: {e}")
    
    async def fetch_comments(self, pr_number: int) -> List[dict]:
        """Fetch comments for a PR"""
        url = f"{self.base_url}/repos/{self.repo}/pulls/{pr_number}/comments"
        
        try:
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching comments for PR {pr_number}: {e}")
            return []
    
    async def fetch_reviews(self, pr_number: int) -> List[dict]:
        """Fetch reviews (approvals) for a PR"""
        url = f"{self.base_url}/repos/{self.repo}/pulls/{pr_number}/reviews"
        
        try:
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching reviews for PR {pr_number}: {e}")
            return []
    
    async def fetch_changes(self, pr_number: int) -> dict:
        """Fetch changes (files) for a PR"""
        url = f"{self.base_url}/repos/{self.repo}/pulls/{pr_number}/files"
        
        try:
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            return {'files': response.json()}
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching changes for PR {pr_number}: {e}")
            return {'files': []}
    
    async def fetch_mr_details(self, pr_number: int) -> dict:
        """Fetch PR details (comments, approvals, changes)"""
        comments = await self.fetch_comments(pr_number)
        reviews = await self.fetch_reviews(pr_number)
        changes = await self.fetch_changes(pr_number)
        
        return {
            'comments': comments,
            'reviews': reviews,
            'changes': changes
        }
