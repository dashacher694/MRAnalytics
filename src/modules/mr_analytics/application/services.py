from typing import List, Dict, Any
from datetime import datetime, timezone
from loguru import logger

from src.modules.mr_analytics.domain.aggregate.model import MergeRequest, MRMetrics
from src.modules.mr_analytics.domain.constants import TimeConstants, ComplexityScoring


class MRAnalyticsService:
    
    def calculate_metrics_from_mr(self, mr: MergeRequest) -> MRMetrics:
        return MRMetrics(
            mr_iid=mr.iid,
            title=mr.title,
            author=mr.author,
            created_at=mr.created_at or datetime.now(timezone.utc),
            merged_at=mr.merged_at or datetime.now(timezone.utc),
            web_url=mr.web_url,
            additions=mr.additions,
            deletions=mr.deletions,
            time_to_merge=self._calculate_time_to_merge(mr),
            review_rounds=self._calculate_review_rounds(mr),
            comment_density=self._calculate_comment_density(mr),
            formal_approval=self._calculate_formal_approval(mr),
            response_time_hours=self._calculate_response_time(mr),
            num_comments=len(mr.comments),
            num_approvals=len(mr.approvals),
            changes_requested=self._calculate_changes_requested(mr),
        )
    
    def _calculate_time_to_merge(self, mr: MergeRequest) -> float | None:
        if mr.created_at and mr.merged_at:
            delta = mr.merged_at - mr.created_at
            return delta.total_seconds() / TimeConstants.SECONDS_PER_HOUR
        return None
    
    def _calculate_review_rounds(self, mr: MergeRequest) -> int:
        if not mr.comments:
            return 0
        reviewers = set(c.author for c in mr.comments if c.author != mr.author)
        return len(reviewers)
    
    def _calculate_comment_density(self, mr: MergeRequest) -> float:
        total_changes = mr.additions + mr.deletions
        if total_changes > 0:
            return len(mr.comments) / total_changes
        return 0.0
    
    def _calculate_formal_approval(self, mr: MergeRequest) -> int:
        has_approval = len(mr.approvals) > 0
        has_comments = len(mr.comments) > 0
        return 1 if (has_approval and not has_comments) else 0
    
    def _calculate_response_time(self, mr: MergeRequest) -> float | None:
        if not mr.comments or not mr.created_at:
            return None
        
        first_comment = min(mr.comments, key=lambda c: c.created_at)
        if first_comment.created_at > mr.created_at:
            delta = first_comment.created_at - mr.created_at
            return delta.total_seconds() / TimeConstants.SECONDS_PER_HOUR
        return None
    
    def _calculate_changes_requested(self, mr: MergeRequest) -> int:
        if not mr.comments:
            return 0
        
        changes_keywords = [
            "requested changes",
            "changes requested", 
            "please fix",
            "needs changes",
            "request changes",
            "change request"
        ]
        
        changes_count = 0
        for comment in mr.comments:
            if comment.author != mr.author:
                comment_lower = comment.body.lower()
                if any(keyword in comment_lower for keyword in changes_keywords):
                    changes_count += 1
        
        return changes_count
    
    def batch_calculate_stats(self, mrs: List[MergeRequest]) -> Dict[str, Any]:
        if not mrs:
            return {
                'total_mrs': 0,
                'total_lines_changed': 0,
                'total_comments': 0,
                'total_approvals': 0,
                'avg_lines_changed': 0,
                'avg_comments': 0,
                'avg_approvals': 0,
            }
        
        total_lines = sum(mr.additions + mr.deletions for mr in mrs)
        total_comments = sum(len(mr.comments) for mr in mrs)
        total_approvals = sum(len(mr.approvals) for mr in mrs)
        
        return {
            'total_mrs': len(mrs),
            'total_lines_changed': total_lines,
            'total_comments': total_comments,
            'total_approvals': total_approvals,
            'avg_lines_changed': total_lines / len(mrs),
            'avg_comments': total_comments / len(mrs),
            'avg_approvals': total_approvals / len(mrs),
        }
    
    def get_top_authors_by_lines(self, mrs: List[MergeRequest], limit: int = ComplexityScoring.DEFAULT_AUTHORS_LIMIT) -> List[Dict[str, Any]]:
        author_stats = {}
        
        for mr in mrs:
            if mr.author not in author_stats:
                author_stats[mr.author] = {
                    'author': mr.author,
                    'total_lines': 0,
                    'mr_count': 0,
                    'additions': 0,
                    'deletions': 0,
                }
            
            author_stats[mr.author]['total_lines'] += mr.additions + mr.deletions
            author_stats[mr.author]['mr_count'] += 1
            author_stats[mr.author]['additions'] += mr.additions
            author_stats[mr.author]['deletions'] += mr.deletions
        
        sorted_authors = sorted(author_stats.values(), key=lambda x: x['total_lines'], reverse=True)
        return sorted_authors[:limit]
    
    def filter_mrs_by_date_range(self, mrs: List[MergeRequest], start_date: datetime, end_date: datetime) -> List[MergeRequest]:
        return [
            mr for mr in mrs 
            if mr.created_at and start_date <= mr.created_at <= end_date
        ]
    
    def get_mr_complexity_score(self, mr: MergeRequest) -> float:
        lines_score = min((mr.additions + mr.deletions) / ComplexityScoring.LINES_CHANGED_DIVISOR, 1.0)
        comments_score = min(len(mr.comments) / ComplexityScoring.COMMENTS_DIVISOR, 1.0)
        approvals_score = min(len(mr.approvals) / ComplexityScoring.APPROVALS_DIVISOR, 1.0)
        
        return (lines_score * ComplexityScoring.LINES_WEIGHT + comments_score * ComplexityScoring.COMMENTS_WEIGHT + approvals_score * ComplexityScoring.APPROVALS_WEIGHT)
