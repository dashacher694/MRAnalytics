"""
Tests for GetMetrics UseCase
"""
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, Mock
import pytest

from src.modules.mr_analytics.usecase.get_metrics.impl import GetMetricsUseCase
from src.modules.mr_analytics.usecase.get_metrics.command import GetMetricsRequest, GetMetricsResponse
from src.modules.mr_analytics.domain.aggregate.model import MRMetrics, RiskScore
from src.modules.utils.errors import NotFoundError, BadRequestError


@pytest.fixture
def mock_uow():
    """Mock Unit of Work"""
    uow = Mock()
    uow.metrics_repository = AsyncMock()
    return uow


@pytest.fixture
def usecase(mock_uow):
    """GetMetrics usecase instance"""
    return GetMetricsUseCase(mock_uow)


@pytest.fixture
def sample_metrics():
    """Sample MRMetrics data"""
    return [
        MRMetrics(
            mr_iid=1,
            title="Test MR 1",
            author="author1",
            created_at=datetime(2024, 1, 1),
            merged_at=datetime(2024, 1, 2),
            web_url="https://gitlab.com/test/1",
            additions=100,
            deletions=50,
            time_to_merge=24.0,
            review_rounds=2,
            comment_density=0.02,
            formal_approval=0,
            response_time_hours=2.0,
            num_comments=3,
            num_approvals=2,
            risk_score=RiskScore.LOW
        ),
        MRMetrics(
            mr_iid=2,
            title="Test MR 2",
            author="author2",
            created_at=datetime(2024, 1, 3),
            merged_at=datetime(2024, 1, 4),
            web_url="https://gitlab.com/test/2",
            additions=200,
            deletions=100,
            time_to_merge=48.0,
            review_rounds=3,
            comment_density=0.03,
            formal_approval=1,
            response_time_hours=4.0,
            num_comments=9,
            num_approvals=1,
            risk_score=RiskScore.MEDIUM
        )
    ]


class TestGetMetricsUseCase:
    
    @pytest.mark.asyncio
    async def test_get_metrics_by_mr_iid_success(self, usecase, mock_uow, sample_metrics):
        """Test successful metrics retrieval by MR IID"""
        # Arrange
        mr_iid = 1
        mock_uow.metrics_repository.get_by_iid.return_value = sample_metrics[0]
        request = GetMetricsRequest(mr_iid=mr_iid)
        
        # Act
        result = await usecase.invoke(request)
        
        # Assert
        assert isinstance(result, GetMetricsResponse)
        assert result.total == 1
        assert len(result.metrics) == 1
        assert result.metrics[0]['mr_iid'] == mr_iid
        mock_uow.metrics_repository.get_by_iid.assert_called_once_with(mr_iid)
    
    @pytest.mark.asyncio
    async def test_get_metrics_by_mr_iid_not_found(self, usecase, mock_uow):
        """Test 404 when MR IID not found"""
        # Arrange
        mr_iid = 999
        mock_uow.metrics_repository.get_by_iid.return_value = None
        request = GetMetricsRequest(mr_iid=mr_iid)
        
        # Act & Assert
        with pytest.raises(NotFoundError, match="Metrics not found for MR IID: 999"):
            await usecase.invoke(request)
    
    @pytest.mark.asyncio
    async def test_get_metrics_by_author_success(self, usecase, mock_uow, sample_metrics):
        """Test successful metrics retrieval by author"""
        # Arrange
        author = "author1"
        author_metrics = [m for m in sample_metrics if m.author == author]
        mock_uow.metrics_repository.get_by_author.return_value = author_metrics
        request = GetMetricsRequest(author=author)
        
        # Act
        result = await usecase.invoke(request)
        
        # Assert
        assert isinstance(result, GetMetricsResponse)
        assert result.total == 1
        assert len(result.metrics) == 1
        assert result.metrics[0]['author'] == author
        mock_uow.metrics_repository.get_by_author.assert_called_once_with(author)
    
    @pytest.mark.asyncio
    async def test_get_metrics_by_author_not_found(self, usecase, mock_uow):
        """Test 404 when author not found"""
        # Arrange
        author = "nonexistent_author"
        mock_uow.metrics_repository.get_by_author.return_value = []
        request = GetMetricsRequest(author=author)
        
        # Act & Assert
        with pytest.raises(NotFoundError, match="Metrics not found for author: nonexistent_author"):
            await usecase.invoke(request)
    
    @pytest.mark.asyncio
    async def test_get_metrics_by_date_range_success(self, usecase, mock_uow, sample_metrics):
        """Test successful metrics retrieval by date range"""
        # Arrange
        days = 30
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        mock_uow.metrics_repository.get_by_date_range.return_value = sample_metrics
        request = GetMetricsRequest(days=days)
        
        # Act
        result = await usecase.invoke(request)
        
        # Assert
        assert isinstance(result, GetMetricsResponse)
        assert result.total == 2
        assert len(result.metrics) == 2
        mock_uow.metrics_repository.get_by_date_range.assert_called_once()
        
        # Verify date range calculation
        call_args = mock_uow.metrics_repository.get_by_date_range.call_args[0]
        assert call_args[0] == start_date
        assert call_args[1] == end_date
    
    @pytest.mark.asyncio
    async def test_get_metrics_by_date_range_not_found(self, usecase, mock_uow):
        """Test 404 when no metrics found in date range"""
        # Arrange
        days = 7
        mock_uow.metrics_repository.get_by_date_range.return_value = []
        request = GetMetricsRequest(days=days)
        
        # Act & Assert
        with pytest.raises(NotFoundError, match="No metrics found in the last 7 days"):
            await usecase.invoke(request)
    
    @pytest.mark.asyncio
    async def test_get_metrics_invalid_days_too_low(self, usecase):
        """Test 400 when days parameter is too low"""
        # Arrange
        request = GetMetricsRequest(days=0)
        
        # Act & Assert
        with pytest.raises(BadRequestError, match="Days parameter must be between 1 and 365"):
            await usecase.invoke(request)
    
    @pytest.mark.asyncio
    async def test_get_metrics_invalid_days_too_high(self, usecase):
        """Test 400 when days parameter is too high"""
        # Arrange
        request = GetMetricsRequest(days=366)
        
        # Act & Assert
        with pytest.raises(BadRequestError, match="Days parameter must be between 1 and 365"):
            await usecase.invoke(request)
    
    @pytest.mark.asyncio
    async def test_get_metrics_priority_mr_iid_over_author(self, usecase, mock_uow, sample_metrics):
        """Test that MR IID filter takes priority over author filter"""
        # Arrange
        mr_iid = 1
        author = "different_author"
        mock_uow.metrics_repository.get_by_iid.return_value = sample_metrics[0]
        request = GetMetricsRequest(mr_iid=mr_iid, author=author)
        
        # Act
        result = await usecase.invoke(request)
        
        # Assert
        assert result.total == 1
        mock_uow.metrics_repository.get_by_iid.assert_called_once_with(mr_iid)
        mock_uow.metrics_repository.get_by_author.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_get_metrics_priority_author_over_date_range(self, usecase, mock_uow, sample_metrics):
        """Test that author filter takes priority over date range filter"""
        # Arrange
        author = "author1"
        author_metrics = [m for m in sample_metrics if m.author == author]
        mock_uow.metrics_repository.get_by_author.return_value = author_metrics
        request = GetMetricsRequest(author=author, days=30)
        
        # Act
        result = await usecase.invoke(request)
        
        # Assert
        assert result.total == 1
        mock_uow.metrics_repository.get_by_author.assert_called_once_with(author)
        mock_uow.metrics_repository.get_by_date_range.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_get_metrics_response_structure(self, usecase, mock_uow, sample_metrics):
        """Test response structure contains expected fields"""
        # Arrange
        mock_uow.metrics_repository.get_by_date_range.return_value = sample_metrics
        request = GetMetricsRequest(days=30)
        
        # Act
        result = await usecase.invoke(request)
        
        # Assert
        assert hasattr(result, 'metrics')
        assert hasattr(result, 'total')
        assert isinstance(result.metrics, list)
        assert isinstance(result.total, int)
        assert len(result.metrics) == result.total
        
        # Check metric structure
        metric = result.metrics[0]
        assert 'mr_iid' in metric
        assert 'title' in metric
        assert 'author' in metric
        assert 'risk_score' in metric
