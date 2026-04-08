"""
GitLab API client implementation
"""
import requests
from datetime import datetime, timedelta
from typing import List
from loguru import logger

from src.modules.mr_analytics.domain.aggregate.model import MergeRequest
from src.modules.mr_analytics.domain.value_objects import Comment
from src.infrastructure.clients.base import VCSClient
from src.core.errors import APIError


class GitLabClient(VCSClient):
    """GitLab API client"""
    
    def __init__(self, token: str, base_url: str, project_id: int, timeout: int = 30):
        self.token = token
        self.base_url = base_url
        self.project_id = project_id
        self.timeout = timeout
        self.headers = {'PRIVATE-TOKEN': token}
    
    async def fetch_merge_requests(self, state: str = "merged", created_after: datetime = None, created_before: datetime = None) -> List[dict]:
        """Fetch MRs from GitLab as raw dict data"""
        params = {
            'state': state,
            'per_page': 20,
            'page': 1,
            'order_by': 'created_at',
            'sort': 'desc'
        }
        
        if created_after:
            params['created_after'] = created_after.isoformat()
        if created_before:
            params['created_before'] = created_before.isoformat()
        
        mrs = []
        page = 1
        
        while True:
            params['page'] = page
            url = f"{self.base_url}/api/v4/projects/{self.project_id}/merge_requests"
            
            try:
                response = requests.get(url, headers=self.headers, params=params, timeout=self.timeout)
                response.raise_for_status()
            except requests.RequestException as e:
                raise APIError(f"GitLab API error: {e}")
            
            data = response.json()
            
            if not data:
                break
            
            mrs.extend(data)
            page += 1
            
            if page > 100:  # Safety limit
                break
        
        logger.info(f"Fetched {len(mrs)} MRs from GitLab")
        return mrs
    
    async def fetch_comments(self, mr_iid: int) -> List[dict]:
        """Fetch comments for a specific MR"""
        comments = []
        try:
            discussions_url = f"{self.base_url}/api/v4/projects/{self.project_id}/merge_requests/{mr_iid}/discussions"
            response = requests.get(discussions_url, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            
            discussions = response.json()
            for discussion in discussions:
                for note in discussion.get('notes', []):
                    if not note.get('system', False):
                        comments.append(note)
        except requests.RequestException as e:
            logger.warning(f"Failed to fetch comments for MR !{mr_iid}: {e}")
        
        return comments
    
    async def fetch_approvals(self, mr_iid: int) -> List[dict]:
        """Fetch approvals for a specific MR"""
        approvals = []
        try:
            approvals_url = f"{self.base_url}/api/v4/projects/{self.project_id}/merge_requests/{mr_iid}/approvals"
            response = requests.get(approvals_url, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            
            approvals_data = response.json()
            approvals = approvals_data.get('approved_by', [])
        except requests.RequestException as e:
            logger.warning(f"Failed to fetch approvals for MR !{mr_iid}: {e}")
        
        return approvals
    
    async def fetch_changes(self, mr_iid: int) -> List[dict]:
        """Fetch file changes for a specific MR"""
        changes = []
        try:
            changes_url = f"{self.base_url}/api/v4/projects/{self.project_id}/merge_requests/{mr_iid}/changes"
            response = requests.get(changes_url, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            
            changes_data = response.json()
            
            # Calculate additions/deletions from diff
            for change in changes_data.get('changes', []):
                diff = change.get('diff', '')
                additions = diff.count('\n+') - diff.count('\n+++')
                deletions = diff.count('\n-') - diff.count('\n---')
                changes.append({
                    'additions': max(0, additions),
                    'deletions': max(0, deletions),
                    'new_path': change.get('new_path', ''),
                    'old_path': change.get('old_path', '')
                })
        except requests.RequestException as e:
            logger.warning(f"Failed to fetch changes for MR !{mr_iid}: {e}")
        
        return changes
    
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
