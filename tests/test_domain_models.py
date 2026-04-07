"""
Tests for Domain Models and Value Objects
"""
from datetime import datetime
import pytest
import uuid

from src.modules.mr_analytics.domain.aggregate.model import MergeRequest, MRMetrics, RiskScore
from src.modules.mr_analytics.domain.value_objects import Comment, Approval, ReviewRound


class TestRiskScore:
    """Test RiskScore enum"""
    
    def test_risk_score_values(self):
        """Test RiskScore enum has correct values"""
        assert RiskScore.HIGH.value == "high"
        assert RiskScore.MEDIUM.value == "medium"
        assert RiskScore.LOW.value == "low"
    
    def test_risk_score_comparison(self):
        """Test RiskScore enum comparison"""
        assert RiskScore.HIGH != RiskScore.MEDIUM
        assert RiskScore.MEDIUM != RiskScore.LOW
        assert RiskScore.LOW != RiskScore.HIGH
        assert RiskScore.HIGH == RiskScore.HIGH


class TestComment:
    """Test Comment value object"""
    
    def test_comment_creation(self):
        """Test Comment creation with default values"""
        comment = Comment()
        
        assert isinstance(comment.id, uuid.UUID)
        assert comment.author == ""
        assert isinstance(comment.created_at, datetime)
        assert comment.body == ""
        assert comment.resolvable is False
    
    def test_comment_creation_with_values(self):
        """Test Comment creation with specific values"""
        test_id = uuid.uuid4()
        test_time = datetime(2024, 1, 1, 12, 0, 0)
        
        comment = Comment(
            id=test_id,
            author="reviewer1",
            created_at=test_time,
            body="LGTM",
            resolvable=False
        )
        
        assert comment.id == test_id
        assert comment.author == "reviewer1"
        assert comment.created_at == test_time
        assert comment.body == "LGTM"
        assert comment.resolvable is False
    
    def test_comment_equality(self):
        """Test Comment equality based on ID"""
        test_id = uuid.uuid4()
        
        comment1 = Comment(id=test_id, author="author1", body="Comment 1")
        comment2 = Comment(id=test_id, author="author2", body="Comment 2")
        comment3 = Comment(author="author1", body="Comment 1")
        
        # Comments with same ID should be equal (dataclass behavior)
        assert comment1.id == comment2.id
        assert comment1.id != comment3.id


class TestApproval:
    """Test Approval value object"""
    
    def test_approval_creation(self):
        """Test Approval creation with default values"""
        approval = Approval()
        
        assert isinstance(approval.id, uuid.UUID)
        assert approval.approver == ""
        assert isinstance(approval.approved_at, datetime)
    
    def test_approval_creation_with_values(self):
        """Test Approval creation with specific values"""
        test_id = uuid.uuid4()
        test_time = datetime(2024, 1, 1, 14, 0, 0)
        
        approval = Approval(
            id=test_id,
            approver="reviewer1",
            approved_at=test_time
        )
        
        assert approval.id == test_id
        assert approval.approver == "reviewer1"
        assert approval.approved_at == test_time


class TestReviewRound:
    """Test ReviewRound value object"""
    
    def test_review_round_creation(self):
        """Test ReviewRound creation with default values"""
        round_obj = ReviewRound()
        
        assert isinstance(round_obj.id, uuid.UUID)
        assert round_obj.round_number == 0
        assert isinstance(round_obj.started_at, datetime)
        assert round_obj.completed_at is None
    
    def test_review_round_creation_with_values(self):
        """Test ReviewRound creation with specific values"""
        test_id = uuid.uuid4()
        start_time = datetime(2024, 1, 1, 10, 0, 0)
        end_time = datetime(2024, 1, 1, 12, 0, 0)
        
        round_obj = ReviewRound(
            id=test_id,
            round_number=2,
            started_at=start_time,
            completed_at=end_time
        )
        
        assert round_obj.id == test_id
        assert round_obj.round_number == 2
        assert round_obj.started_at == start_time
        assert round_obj.completed_at == end_time


class TestMergeRequest:
    """Test MergeRequest aggregate"""
    
    def test_merge_request_creation_defaults(self):
        """Test MergeRequest creation with default values"""
        mr = MergeRequest()
        
        assert mr.iid == 0
        assert mr.title == ""
        assert mr.author == ""
        assert mr.created_at is None
        assert mr.merged_at is None
        assert mr.web_url == ""
        assert mr.additions == 0
        assert mr.deletions == 0
        assert mr.comments == []
        assert mr.approvals == []
        assert mr.changed_files == []
        assert mr.author_mr_count == 0
        assert mr.creation_hour == 0
        assert mr.is_critical_files is False
        assert mr.unique_reviewers == []
        assert mr.risk_score == RiskScore.LOW
    
    def test_merge_request_creation_with_values(self):
        """Test MergeRequest creation with specific values"""
        comment = Comment(author="reviewer1", body="LGTM")
        approval = Approval(approver="reviewer2")
        
        mr = MergeRequest(
            iid=123,
            title="Feature MR",
            author="author1",
            created_at=datetime(2024, 1, 1, 10, 0, 0),
            merged_at=datetime(2024, 1, 2, 14, 0, 0),
            web_url="https://gitlab.com/test/123",
            additions=100,
            deletions=50,
            comments=[comment],
            approvals=[approval],
            changed_files=["file1.py", "file2.py"],
            author_mr_count=5,
            creation_hour=10,
            is_critical_files=True,
            unique_reviewers=["reviewer1", "reviewer2"],
            risk_score=RiskScore.MEDIUM
        )
        
        assert mr.iid == 123
        assert mr.title == "Feature MR"
        assert mr.author == "author1"
        assert mr.created_at == datetime(2024, 1, 1, 10, 0, 0)
        assert mr.merged_at == datetime(2024, 1, 2, 14, 0, 0)
        assert mr.web_url == "https://gitlab.com/test/123"
        assert mr.additions == 100
        assert mr.deletions == 50
        assert len(mr.comments) == 1
        assert mr.comments[0].author == "reviewer1"
        assert len(mr.approvals) == 1
        assert mr.approvals[0].approver == "reviewer2"
        assert mr.changed_files == ["file1.py", "file2.py"]
        assert mr.author_mr_count == 5
        assert mr.creation_hour == 10
        assert mr.is_critical_files is True
        assert mr.unique_reviewers == ["reviewer1", "reviewer2"]
        assert mr.risk_score == RiskScore.MEDIUM
    
    def test_merge_request_multiple_comments(self):
        """Test MergeRequest with multiple comments"""
        comments = [
            Comment(author="reviewer1", body="First comment"),
            Comment(author="reviewer2", body="Second comment"),
            Comment(author="reviewer1", body="Third comment")
        ]
        
        mr = MergeRequest(comments=comments)
        
        assert len(mr.comments) == 3
        assert mr.comments[0].author == "reviewer1"
        assert mr.comments[1].author == "reviewer2"
        assert mr.comments[2].author == "reviewer1"
    
    def test_merge_request_multiple_approvals(self):
        """Test MergeRequest with multiple approvals"""
        approvals = [
            Approval(approver="reviewer1"),
            Approval(approver="reviewer2"),
            Approval(approver="reviewer3")
        ]
        
        mr = MergeRequest(approvals=approvals)
        
        assert len(mr.approvals) == 3
        assert mr.approvals[0].approver == "reviewer1"
        assert mr.approvals[1].approver == "reviewer2"
        assert mr.approvals[2].approver == "reviewer3"


class TestMRMetrics:
    """Test MRMetrics aggregate"""
    
    def test_mr_metrics_creation_defaults(self):
        """Test MRMetrics creation with default values"""
        metrics = MRMetrics()
        
        assert metrics.mr_iid == 0
        assert metrics.title == ""
        assert metrics.author == ""
        assert isinstance(metrics.created_at, datetime)
        assert isinstance(metrics.merged_at, datetime)
        assert metrics.web_url == ""
        assert metrics.additions == 0
        assert metrics.deletions == 0
        assert metrics.time_to_merge is None
        assert metrics.review_rounds == 0
        assert metrics.comment_density == 0.0
        assert metrics.formal_approval == 0
        assert metrics.response_time_hours is None
        assert metrics.num_comments == 0
        assert metrics.num_approvals == 0
        assert metrics.risk_score == RiskScore.LOW
        assert metrics.suggested_reviewers == []
        assert metrics.reviewer_burnout_index == 0.0
        assert metrics.is_anomaly is False
    
    def test_mr_metrics_creation_with_values(self):
        """Test MRMetrics creation with specific values"""
        test_time = datetime(2024, 1, 1, 10, 0, 0)
        
        metrics = MRMetrics(
            mr_iid=456,
            title="Metrics MR",
            author="author2",
            created_at=test_time,
            merged_at=test_time,
            web_url="https://gitlab.com/metrics/456",
            additions=200,
            deletions=100,
            time_to_merge=24.5,
            review_rounds=3,
            comment_density=0.05,
            formal_approval=1,
            response_time_hours=2.5,
            num_comments=10,
            num_approvals=2,
            risk_score=RiskScore.HIGH,
            suggested_reviewers=["reviewer1", "reviewer2"],
            reviewer_burnout_index=0.75,
            is_anomaly=True
        )
        
        assert metrics.mr_iid == 456
        assert metrics.title == "Metrics MR"
        assert metrics.author == "author2"
        assert metrics.created_at == test_time
        assert metrics.merged_at == test_time
        assert metrics.web_url == "https://gitlab.com/metrics/456"
        assert metrics.additions == 200
        assert metrics.deletions == 100
        assert metrics.time_to_merge == 24.5
        assert metrics.review_rounds == 3
        assert metrics.comment_density == 0.05
        assert metrics.formal_approval == 1
        assert metrics.response_time_hours == 2.5
        assert metrics.num_comments == 10
        assert metrics.num_approvals == 2
        assert metrics.risk_score == RiskScore.HIGH
        assert metrics.suggested_reviewers == ["reviewer1", "reviewer2"]
        assert metrics.reviewer_burnout_index == 0.75
        assert metrics.is_anomaly is True
    
    def test_mr_metrics_suggested_reviewers(self):
        """Test MRMetrics with suggested reviewers"""
        reviewers = ["reviewer1", "reviewer2", "reviewer3"]
        metrics = MRMetrics(suggested_reviewers=reviewers)
        
        assert len(metrics.suggested_reviewers) == 3
        assert metrics.suggested_reviewers == reviewers
    
    def test_mr_metrics_burnout_index_bounds(self):
        """Test MRMetrics burnout index within valid bounds"""
        # Test low burnout
        metrics_low = MRMetrics(reviewer_burnout_index=0.1)
        assert 0.0 <= metrics_low.reviewer_burnout_index <= 1.0
        
        # Test high burnout
        metrics_high = MRMetrics(reviewer_burnout_index=0.9)
        assert 0.0 <= metrics_high.reviewer_burnout_index <= 1.0
        
        # Test edge cases
        metrics_zero = MRMetrics(reviewer_burnout_index=0.0)
        metrics_max = MRMetrics(reviewer_burnout_index=1.0)
        assert metrics_zero.reviewer_burnout_index == 0.0
        assert metrics_max.reviewer_burnout_index == 1.0
