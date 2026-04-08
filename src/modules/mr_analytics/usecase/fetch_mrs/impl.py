from typing import List
from datetime import datetime, timedelta
from loguru import logger

from src.modules.seedwork.base_usecase import BaseUseCase, async_transactional
from src.infrastructure.clients.gitlab import GitLabClient
from src.modules.mr_analytics.infrastructure.dto import VCSMergeRequestData, CommentData, ApprovalData
from src.modules.mr_analytics.usecase.fetch_mrs.command import (
    FetchMergeRequestsCommand,
    FetchMergeRequestsResponse
)
from src.core.config import settings


class FetchMergeRequestsUseCase(BaseUseCase):
    
    def __init__(self, vcs_client: GitLabClient):
        self._vcs_client = vcs_client
    
    @async_transactional(read_only=True)
    async def invoke(self, command: FetchMergeRequestsCommand) -> FetchMergeRequestsResponse:
        logger.info(f"Fetching MRs from {settings.vcs_provider.value} for last {command.days} days")
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=command.days)
        
        try:
            raw_mrs = await self._vcs_client.fetch_merge_requests(
                state="merged",
                created_after=start_date,
                created_before=end_date
            )
            
            logger.info(f"Fetched {len(raw_mrs)} MRs from VCS")
            
            vcs_mrs = []
            for mr_data in raw_mrs:
                comments = await self._vcs_client.fetch_comments(mr_data['iid'])
                approvals = await self._vcs_client.fetch_approvals(mr_data['iid'])
                changes = await self._vcs_client.fetch_changes(mr_data['iid'])
                
                comment_dtos = [
                    CommentData(
                        author=c.get('author', {}).get('username', 'unknown'),
                        created_at=c.get('created_at', ''),
                        body=c.get('body', ''),
                        resolvable=c.get('resolvable', False)
                    )
                    for c in comments
                ]
                
                approval_dtos = [
                    ApprovalData(
                        approver=a.get('user', {}).get('username', 'unknown'),
                        approved_at=a.get('created_at', '')
                    )
                    for a in approvals
                ]
                
                additions = sum(change.get('additions', 0) for change in changes)
                deletions = sum(change.get('deletions', 0) for change in changes)
                
                vcs_mr = VCSMergeRequestData(
                    iid=mr_data['iid'],
                    title=mr_data['title'],
                    author=mr_data.get('author', {}).get('username', 'unknown'),
                    created_at=mr_data.get('created_at', ''),
                    merged_at=mr_data.get('merged_at', ''),
                    web_url=mr_data.get('web_url', ''),
                    additions=additions,
                    deletions=deletions,
                    comments=comment_dtos,
                    approvals=approval_dtos
                )
                vcs_mrs.append(vcs_mr)
            
            logger.success(f"Successfully fetched and converted {len(vcs_mrs)} MRs")
            
            return FetchMergeRequestsResponse(
                mrs=vcs_mrs,
                total_fetched=len(vcs_mrs)
            )
            
        except Exception as e:
            logger.error(f"Error fetching MRs from VCS: {e}")
            raise
