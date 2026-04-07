from typing import List, Dict, Any
from datetime import datetime
from uuid import uuid4
from loguru import logger

from pymfdata.common.usecase import BaseUseCase
from pymfdata.rdb.transaction import async_transactional

from src.modules.mr_analytics.domain.aggregate.model import MergeRequest, MRMetrics
from src.modules.mr_analytics.domain.value_objects import Comment, Approval
from src.modules.mr_analytics.application.services import MRAnalyticsService
from src.modules.mr_analytics.infrastructure.persistence.uow import MRPersistenceUnitOfWork
from src.modules.mr_analytics.usecase.process_mrs.command import ProcessMergeRequestsCommand
from src.modules.mr_analytics.infrastructure.dto import VCSMergeRequestData, ProcessedMergeRequestDTO, ProcessMergeRequestsResponse


class ProcessMergeRequestsUseCase(BaseUseCase[MRPersistenceUnitOfWork]):
    
    def __init__(self, uow: MRPersistenceUnitOfWork) -> None:
        self._uow = uow
        self._analytics_service = MRAnalyticsService()
    
    @staticmethod
    def _parse_datetime(dt_str: str | None) -> datetime | None:
        if not dt_str:
            return None
        return datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
    
    def _convert_vcs_to_domain(self, vcs_data: VCSMergeRequestData) -> MergeRequest:
        comments = []
        for comment_data in vcs_data.comments:
            comment = Comment(
                id=uuid4(),
                author=comment_data.author,
                created_at=self._parse_datetime(comment_data.created_at) or datetime.now(),
                body=comment_data.body,
                resolvable=comment_data.resolvable,
            )
            comments.append(comment)
        
        approvals = []
        for approval_data in vcs_data.approvals:
            approval = Approval(
                id=uuid4(),
                approver=approval_data.approver,
                approved_at=self._parse_datetime(approval_data.approved_at) or datetime.now(),
            )
            approvals.append(approval)
        
        return MergeRequest(
            iid=vcs_data.iid,
            title=vcs_data.title,
            author=vcs_data.author,
            created_at=self._parse_datetime(vcs_data.created_at),
            merged_at=self._parse_datetime(vcs_data.merged_at),
            web_url=vcs_data.web_url,
            additions=vcs_data.additions,
            deletions=vcs_data.deletions,
            comments=comments,
            approvals=approvals,
        )
    
    def _convert_domain_to_dto(self, mr: MergeRequest) -> ProcessedMergeRequestDTO:
        return ProcessedMergeRequestDTO(
            iid=mr.iid,
            title=mr.title,
            author=mr.author,
            created_at=mr.created_at or datetime.now(),
            merged_at=mr.merged_at or datetime.now(),
            web_url=mr.web_url,
            additions=mr.additions,
            deletions=mr.deletions,
            num_comments=len(mr.comments),
            num_approvals=len(mr.approvals),
            total_lines_changed=mr.additions + mr.deletions,
        )
    
    @async_transactional()
    async def invoke(self, command: ProcessMergeRequestsCommand) -> ProcessMergeRequestsResponse:
        logger.info(f"Processing {len(command.mrs)} MRs from VCS")
        
        domain_mrs = [
            self._convert_vcs_to_domain(vcs_data) 
            for vcs_data in command.mrs
        ]
        
        metrics = []
        for mr in domain_mrs:
            metric = self._analytics_service.calculate_metrics(mr)
            metrics.append(metric)
        
        await self._uow.metrics_repository.save_all(metrics)
        
        processed_dtos = [
            self._convert_domain_to_dto(mr) 
            for mr in domain_mrs
        ]
        
        logger.success(f"Processed and saved {len(metrics)} metrics")
        
        return ProcessMergeRequestsResponse(
            processed_mrs=processed_dtos,
            total_processed=len(processed_dtos)
        )
