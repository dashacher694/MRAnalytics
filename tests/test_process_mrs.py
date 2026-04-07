"""
Tests for ProcessMergeRequests UseCase
"""
from unittest.mock import AsyncMock, Mock, patch
import pytest
from datetime import datetime

from src.modules.mr_analytics.usecase.process_mrs.impl import ProcessMergeRequestsUseCase
from src.modules.mr_analytics.usecase.process_mrs.command import ProcessMergeRequestsCommand, ProcessMergeRequestsResponse
from src.modules.mr_analytics.infrastructure.dto import VCSMergeRequestData
from src.modules.mr_analytics.domain.aggregate.model import MRMetrics, RiskScore


@pytest.fixture
def mock_uow():
    """Mock Unit of Work"""
    uow = Mock()
    uow.metrics_repository = AsyncMock()
    return uow


@pytest.fixture
def usecase(mock_uow):
    """ProcessMergeRequests usecase instance"""
    return ProcessMergeRequestsUseCase(mock_uow)


@pytest.fixture
def sample_vcs_mr_data():
    """Sample VCS MR data"""
    return [
        VCSMergeRequestData(
            iid=1,
            title="Backend Feature",
            author="author1",
            created_at=datetime(2024, 1, 1, 10, 0, 0),
            merged_at=datetime(2024, 1, 2, 14, 0, 0),
            web_url="https://gitlab.com/test/1",
            additions=100,
            deletions=50,
            changed_files=["backend/service.py", "backend/models.py"],
            comments=[
                {"author": "reviewer1", "body": "LGTM", "created_at": datetime(2024, 1, 1, 12, 0, 0)},
                {"author": "reviewer2", "body": "Needs changes", "created_at": datetime(2024, 1, 1, 15, 0, 0)}
            ],
            approvals=["reviewer1", "reviewer2"]
        ),
        VCSMergeRequestData(
            iid=2,
            title="Frontend Bugfix",
            author="author2",
            created_at=datetime(2024, 1, 3, 9, 0, 0),
            merged_at=datetime(2024, 1, 4, 11, 0, 0),
            web_url="https://gitlab.com/test/2",
            additions=25,
            deletions=10,
            changed_files=["frontend/components.js"],
            comments=[
                {"author": "reviewer3", "body": "Looks good", "created_at": datetime(2024, 1, 3, 10, 0, 0)}
            ],
            approvals=["reviewer3"]
        )
    ]


class TestProcessMergeRequestsUseCase:
    
    @pytest.mark.asyncio
    async def test_process_mrs_success(self, usecase, mock_uow, sample_vcs_mr_data):
        """Test successful MR processing"""
        # Arrange
        command = ProcessMergeRequestsCommand(mrs=sample_vcs_mr_data)
        
        with patch('src.modules.mr_analytics.application.analytics_services.MetricsCalculationService') as mock_service:
            # Mock service to return calculated metrics
            mock_service.calculate_metrics.side_effect = [
                MRMetrics(
                    mr_iid=1,
                    title="Backend Feature",
                    author="author1",
                    created_at=datetime(2024, 1, 1, 10, 0, 0),
                    merged_at=datetime(2024, 1, 2, 14, 0, 0),
                    web_url="https://gitlab.com/test/1",
                    additions=100,
                    deletions=50,
                    time_to_merge=28.0,
                    review_rounds=2,
                    comment_density=0.02,
                    formal_approval=0,
                    response_time_hours=2.0,
                    num_comments=2,
                    num_approvals=2,
                    risk_score=RiskScore.LOW
                ),
                MRMetrics(
                    mr_iid=2,
                    title="Frontend Bugfix",
                    author="author2",
                    created_at=datetime(2024, 1, 3, 9, 0, 0),
                    merged_at=datetime(2024, 1, 4, 11, 0, 0),
                    web_url="https://gitlab.com/test/2",
                    additions=25,
                    deletions=10,
                    time_to_merge=26.0,
                    review_rounds=1,
                    comment_density=0.04,
                    formal_approval=0,
                    response_time_hours=1.0,
                    num_comments=1,
                    num_approvals=1,
                    risk_score=RiskScore.LOW
                )
            ]
            
            # Act
            result = await usecase.invoke(command)
            
            # Assert
            assert isinstance(result, ProcessMergeRequestsResponse)
            assert result.processed_count == 2
            assert result.failed_count == 0
            assert len(result.processed_mrs) == 2
            assert len(result.failed_mrs) == 0
            
            # Verify service was called for each MR
            assert mock_service.calculate_metrics.call_count == 2
            
            # Verify processed MRs structure
            for mr in result.processed_mrs:
                assert hasattr(mr, 'mr_iid')
                assert hasattr(mr, 'title')
                assert hasattr(mr, 'author')
    
    @pytest.mark.asyncio
    async def test_process_mrs_empty_list(self, usecase, mock_uow):
        """Test MR processing with empty list"""
        # Arrange
        command = ProcessMergeRequestsCommand(mrs=[])
        
        # Act
        result = await usecase.invoke(command)
        
        # Assert
        assert isinstance(result, ProcessMergeRequestsResponse)
        assert result.processed_count == 0
        assert result.failed_count == 0
        assert len(result.processed_mrs) == 0
        assert len(result.failed_mrs) == 0
    
    @pytest.mark.asyncio
    async def test_process_mrs_partial_failure(self, usecase, mock_uow, sample_vcs_mr_data):
        """Test MR processing with partial failures"""
        # Arrange
        command = ProcessMergeRequestsCommand(mrs=sample_vcs_mr_data)
        
        with patch('src.modules.mr_analytics.application.analytics_services.MetricsCalculationService') as mock_service:
            # First MR succeeds, second fails
            mock_service.calculate_metrics.side_effect = [
                MRMetrics(mr_iid=1, title="Backend Feature", author="author1"),
                Exception("Processing failed")
            ]
            
            # Act
            result = await usecase.invoke(command)
            
            # Assert
            assert isinstance(result, ProcessMergeRequestsResponse)
            assert result.processed_count == 1
            assert result.failed_count == 1
            assert len(result.processed_mrs) == 1
            assert len(result.failed_mrs) == 1
            
            # Verify failed MR info
            failed_mr = result.failed_mrs[0]
            assert failed_mr.mr_iid == 2
            assert failed_mr.title == "Frontend Bugfix"
            assert "Processing failed" in failed_mr.error
    
    @pytest.mark.asyncio
    async def test_process_mrs_all_failures(self, usecase, mock_uow, sample_vcs_mr_data):
        """Test MR processing when all fail"""
        # Arrange
        command = ProcessMergeRequestsCommand(mrs=sample_vcs_mr_data)
        
        with patch('src.modules.mr_analytics.application.analytics_services.MetricsCalculationService') as mock_service:
            mock_service.calculate_metrics.side_effect = Exception("Service unavailable")
            
            # Act
            result = await usecase.invoke(command)
            
            # Assert
            assert isinstance(result, ProcessMergeRequestsResponse)
            assert result.processed_count == 0
            assert result.failed_count == 2
            assert len(result.processed_mrs) == 0
            assert len(result.failed_mrs) == 2
            
            # Verify all MRs failed
            failed_iids = [mr.mr_iid for mr in result.failed_mrs]
            assert 1 in failed_iids
            assert 2 in failed_iids
    
    @pytest.mark.asyncio
    async def test_process_mrs_validation_error(self, usecase, mock_uow):
        """Test MR processing with invalid data"""
        # Arrange
        invalid_mr = VCSMergeRequestData(
            iid=-1,  # Invalid IID
            title="",  # Empty title
            author="",  # Empty author
            created_at=datetime.now(),
            merged_at=datetime.now(),
            web_url="invalid-url",
            additions=-1,  # Invalid additions
            deletions=-1,  # Invalid deletions
            changed_files=[],
            comments=[],
            approvals=[]
        )
        command = ProcessMergeRequestsCommand(mrs=[invalid_mr])
        
        # Act
        result = await usecase.invoke(command)
        
        # Assert
        assert isinstance(result, ProcessMergeRequestsResponse)
        assert result.processed_count == 0
        assert result.failed_count == 1
        assert len(result.failed_mrs) == 1
        
        failed_mr = result.failed_mrs[0]
        assert failed_mr.mr_iid == -1
        assert "validation" in failed_mr.error.lower() or "invalid" in failed_mr.error.lower()
    
    @pytest.mark.asyncio
    async def test_process_mrs_large_batch(self, usecase, mock_uow):
        """Test MR processing with large batch"""
        # Arrange
        large_batch = [
            VCSMergeRequestData(
                iid=i,
                title=f"MR {i}",
                author=f"author{i}",
                created_at=datetime(2024, 1, 1),
                merged_at=datetime(2024, 1, 2),
                web_url=f"https://gitlab.com/test/{i}",
                additions=100,
                deletions=50,
                changed_files=[f"file{i}.py"],
                comments=[],
                approvals=[]
            )
            for i in range(1, 101)  # 100 MRs
        ]
        command = ProcessMergeRequestsCommand(mrs=large_batch)
        
        with patch('src.modules.mr_analytics.application.analytics_services.MetricsCalculationService') as mock_service:
            # Mock successful processing for all
            mock_service.calculate_metrics.return_value = MRMetrics(mr_iid=1, title="Test", author="author")
            
            # Act
            result = await usecase.invoke(command)
            
            # Assert
            assert result.processed_count == 100
            assert result.failed_count == 0
            assert len(result.processed_mrs) == 100
            assert mock_service.calculate_metrics.call_count == 100
    
    @pytest.mark.asyncio
    async def test_process_mrs_response_structure(self, usecase, mock_uow, sample_vcs_mr_data):
        """Test MR processing response structure"""
        # Arrange
        command = ProcessMergeRequestsCommand(mrs=sample_vcs_mr_data)
        
        with patch('src.modules.mr_analytics.application.analytics_services.MetricsCalculationService') as mock_service:
            mock_service.calculate_metrics.return_value = MRMetrics(mr_iid=1, title="Test", author="author")
            
            # Act
            result = await usecase.invoke(command)
            
            # Assert
            assert hasattr(result, 'processed_count')
            assert hasattr(result, 'failed_count')
            assert hasattr(result, 'processed_mrs')
            assert hasattr(result, 'failed_mrs')
            
            assert isinstance(result.processed_count, int)
            assert isinstance(result.failed_count, int)
            assert isinstance(result.processed_mrs, list)
            assert isinstance(result.failed_mrs, list)
            
            # Verify counts match lists lengths
            assert result.processed_count == len(result.processed_mrs)
            assert result.failed_count == len(result.failed_mrs)
    
    @pytest.mark.asyncio
    async def test_process_mrs_different_mr_complexity(self, usecase, mock_uow):
        """Test MR processing with different complexity levels"""
        # Arrange
        simple_mr = VCSMergeRequestData(
            iid=1,
            title="Simple fix",
            author="author1",
            created_at=datetime(2024, 1, 1),
            merged_at=datetime(2024, 1, 2),
            web_url="https://gitlab.com/test/1",
            additions=10,
            deletions=5,
            changed_files=["simple.py"],
            comments=[],
            approvals=["reviewer1"]
        )
        
        complex_mr = VCSMergeRequestData(
            iid=2,
            title="Complex feature",
            author="author2",
            created_at=datetime(2024, 1, 1),
            merged_at=datetime(2024, 1, 3),
            web_url="https://gitlab.com/test/2",
            additions=500,
            deletions=200,
            changed_files=["file1.py", "file2.py", "file3.py", "file4.py", "file5.py"],
            comments=[
                {"author": "reviewer1", "body": "Comment 1", "created_at": datetime(2024, 1, 1, 12, 0, 0)},
                {"author": "reviewer2", "body": "Comment 2", "created_at": datetime(2024, 1, 1, 14, 0, 0)},
                {"author": "reviewer3", "body": "Comment 3", "created_at": datetime(2024, 1, 2, 9, 0, 0)}
            ],
            approvals=["reviewer1", "reviewer2", "reviewer3"]
        )
        
        command = ProcessMergeRequestsCommand(mrs=[simple_mr, complex_mr])
        
        with patch('src.modules.mr_analytics.application.analytics_services.MetricsCalculationService') as mock_service:
            def calculate_metrics(vcs_mr):
                if vcs_mr.iid == 1:
                    return MRMetrics(mr_iid=1, title="Simple fix", author="author1", risk_score=RiskScore.LOW)
                else:
                    return MRMetrics(mr_iid=2, title="Complex feature", author="author2", risk_score=RiskScore.HIGH)
            
            mock_service.calculate_metrics.side_effect = calculate_metrics
            
            # Act
            result = await usecase.invoke(command)
            
            # Assert
            assert result.processed_count == 2
            assert result.failed_count == 0
            
            # Verify risk scores based on complexity
            processed_mrs = {mr.mr_iid: mr for mr in result.processed_mrs}
            assert processed_mrs[1].risk_score == RiskScore.LOW
            assert processed_mrs[2].risk_score == RiskScore.HIGH
