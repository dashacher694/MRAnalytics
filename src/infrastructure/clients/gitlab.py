"""
GitLab API client implementation
"""
import requests
from datetime import datetime, timedelta
from typing import List
from loguru import logger

from src.domain.models import MergeRequest, Comment
from src.infrastructure.clients.base import VCSClient
from src.core.errors import APIError


class GitLabClient(VCSClient):
    """GitLab API client"""
    
    def __init__(self, token: str, base_url: str, project_id: str, timeout: int = 30):
        self.token = token
        self.base_url = base_url
        self.project_id = project_id
        self.timeout = timeout
        self.headers = {'PRIVATE-TOKEN': token}
    
    async def fetch_merge_requests(self, days: int) -> List[MergeRequest]:
        """Fetch closed MRs from GitLab"""
        since_date = (datetime.now() - timedelta(days=days)).isoformat()
        
        mrs = []
        page = 1
        per_page = 20
        
        while True:
            url = f"{self.base_url}/api/v4/projects/{self.project_id}/merge_requests"
            params = {
                'state': 'merged',
                'updated_after': since_date,
                'per_page': per_page,
                'page': page,
                'order_by': 'updated_at',
                'sort': 'desc'
            }
            
            try:
                response = requests.get(url, headers=self.headers, params=params, timeout=self.timeout)
                response.raise_for_status()
            except requests.RequestException as e:
                raise APIError(f"GitLab API error: {e}")
            
            data = response.json()
            
            if not data:
                break
            
            for mr_data in data:
                mr = MergeRequest(
                    iid=mr_data['iid'],
                    title=mr_data['title'],
                    author=mr_data['author']['username'],
                    created_at=mr_data['created_at'],
                    merged_at=mr_data.get('merged_at'),
                    web_url=mr_data['web_url'],
                )
                mrs.append(mr)
            
            page += 1
            
            if page > 100:  # Safety limit
                break
        
        logger.info(f"Fetched {len(mrs)} MRs from GitLab")
        return mrs
    
    async def fetch_mr_details(self, mr_iid: int) -> dict:
        """Fetch MR details: changes, comments, approvals"""
        details = {
            'additions': 0,
            'deletions': 0,
            'comments': [],
            'approvals': []
        }
        
        # Get changes (additions/deletions)
        try:
            changes_url = f"{self.base_url}/api/v4/projects/{self.project_id}/merge_requests/{mr_iid}/changes"
            response = requests.get(changes_url, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            
            changes = response.json()
            for change in changes.get('changes', []):
                diff = change.get('diff', '')
                details['additions'] += diff.count('\n+')
                details['deletions'] += diff.count('\n-')
        except requests.RequestException as e:
            logger.warning(f"Failed to fetch changes for MR !{mr_iid}: {e}")
        
        # Get comments
        try:
            discussions_url = f"{self.base_url}/api/v4/projects/{self.project_id}/merge_requests/{mr_iid}/discussions"
            response = requests.get(discussions_url, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            
            discussions = response.json()
            for discussion in discussions:
                for note in discussion.get('notes', []):
                    if note.get('system', False):
                        continue
                    
                    comment = Comment(
                        author=note['author']['username'],
                        created_at=note['created_at'],
                        body=note['body'],
                        resolvable=note.get('resolvable', False)
                    )
                    details['comments'].append(comment)
        except requests.RequestException as e:
            logger.warning(f"Failed to fetch comments for MR !{mr_iid}: {e}")
        
        # Get approvals
        try:
            approvals_url = f"{self.base_url}/api/v4/projects/{self.project_id}/merge_requests/{mr_iid}/approvals"
            response = requests.get(approvals_url, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            
            approvals_data = response.json()
            details['approvals'] = [a['user']['username'] for a in approvals_data.get('approved_by', [])]
        except requests.RequestException as e:
            logger.warning(f"Failed to fetch approvals for MR !{mr_iid}: {e}")
        
        return details
