"""
Tests for Infrastructure Layer
"""
from unittest.mock import AsyncMock, Mock
import pytest
from datetime import datetime, timedelta

from src.modules.mr_analytics.infrastructure.query.uow import QueryUnitOfWork
from src.modules.mr_analytics.infrastructure.query.repository import MRMetricsQueryRepository
from src.modules.mr_analytics.domain.aggregate.model import MRMetrics, RiskScore


class TestMetricsRepository:
    """Test MetricsRepository"""
    
    @pytest.fixture
    def mock_session(self):
        """Mock database session"""
        session = AsyncMock()
        return session
    
    @pytest.fixture
    def repository(self, mock_session):
        """MetricsRepository instance"""
        return MetricsRepository(mock_session)
    
    @pytest.fixture
    def sample_metrics(self):
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
                risk_score=RiskScore.MEDIUM
            )
        ]
    
    @pytest.mark.asyncio
    async def test_get_by_iid_success(self, repository, mock_session, sample_metrics):
        """Test successful get by IID"""
        # Arrange
        mr_iid = 1
        mock_session.get.return_value = sample_metrics[0]
        
        # Act
        result = await repository.get_by_iid(mr_iid)
        
        # Assert
        assert result is not None
        assert result.mr_iid == mr_iid
        mock_session.get.assert_called_once_with(MRMetrics, mr_iid)
    
    @pytest.mark.asyncio
    async def test_get_by_iid_not_found(self, repository, mock_session):
        """Test get by IID when not found"""
        # Arrange
        mr_iid = 999
        mock_session.get.return_value = None
        
        # Act
        result = await repository.get_by_iid(mr_iid)
        
        # Assert
        assert result is None
        mock_session.get.assert_called_once_with(MRMetrics, mr_iid)
    
    @pytest.mark.asyncio
    async def test_get_by_author_success(self, repository, mock_session, sample_metrics):
        """Test successful get by author"""
        # Arrange
        author = "author1"
        author_metrics = [m for m in sample_metrics if m.author == author]
        mock_result = Mock()
        mock_result.scalars.return_value.all.return_value = author_metrics
        mock_session.execute.return_value = mock_result
        
        # Act
        result = await repository.get_by_author(author)
        
        # Assert
        assert len(result) == 1
        assert result[0].author == author
        assert mock_session.execute.called
    
    @pytest.mark.asyncio
    async def test_get_by_author_not_found(self, repository, mock_session):
        """Test get by author when not found"""
        # Arrange
        author = "nonexistent"
        mock_result = Mock()
        mock_result.scalars.return_value.all.return_value = []
        mock_session.execute.return_value = mock_result
        
        # Act
        result = await repository.get_by_author(author)
        
        # Assert
        assert len(result) == 0
    
    @pytest.mark.asyncio
    async def test_get_by_date_range_success(self, repository, mock_session, sample_metrics):
        """Test successful get by date range"""
        # Arrange
        start_date = datetime(2024, 1, 1)
        end_date = datetime(2024, 1, 5)
        mock_result = Mock()
        mock_result.scalars.return_value.all.return_value = sample_metrics
        mock_session.execute.return_value = mock_result
        
        # Act
        result = await repository.get_by_date_range(start_date, end_date)
        
        # Assert
        assert len(result) == 2
        assert mock_session.execute.called
    
    @pytest.mark.asyncio
    async def test_get_by_date_range_empty(self, repository, mock_session):
        """Test get by date range with no results"""
        # Arrange
        start_date = datetime(2024, 2, 1)
        end_date = datetime(2024, 2, 5)
        mock_result = Mock()
        mock_result.scalars.return_value.all.return_value = []
        mock_session.execute.return_value = mock_result
        
        # Act
        result = await repository.get_by_date_range(start_date, end_date)
        
        # Assert
        assert len(result) == 0


class TestQueryUnitOfWork:
    """Test QueryUnitOfWork"""
    
    @pytest.fixture
    def mock_session_factory(self):
        """Mock session factory"""
        factory = Mock()
        factory.return_value = AsyncMock()
        return factory
    
    @pytest.fixture
    def uow(self, mock_session_factory):
        """QueryUnitOfWork instance"""
        return QueryUnitOfWork(mock_session_factory)
    
    def test_uow_initialization(self, uow, mock_session_factory):
        """Test UOW initialization"""
        assert uow._session_factory == mock_session_factory
        assert uow._session is None
        assert hasattr(uow, 'metrics_repository')
    
    def test_uow_context_manager_entry(self, uow, mock_session_factory):
        """Test UOW context manager entry"""
        # Act
        session = uow.__enter__()
        
        # Assert
        assert session is not None
        assert uow._session is not None
        mock_session_factory.assert_called_once()
    
    def test_uow_context_manager_exit(self, uow, mock_session_factory):
        """Test UOW context manager exit"""
        # Arrange
        session = uow.__enter__()
        session.close = Mock()
        
        # Act
        uow.__exit__(None, None, None)
        
        # Assert
        session.close.assert_called_once()
        assert uow._session is None
    
    def test_metrics_repository_creation(self, uow):
        """Test metrics repository creation"""
        # Arrange
        uow.__enter__()
        
        # Assert
        assert isinstance(uow.metrics_repository, MetricsRepository)
        assert uow.metrics_repository._session == uow._session
    
    def test_uow_session_property(self, uow):
        """Test UOW session property"""
        # Arrange
        session = uow.__enter__()
        
        # Assert
        assert uow.session == session
        
        # Cleanup
        uow.__exit__(None, None, None)
    
    def test_uow_session_property_before_enter(self, uow):
        """Test UOW session property before entering context"""
        # Act & Assert
        with pytest.raises(AttributeError):
            _ = uow.session


class TestInfrastructureDTOs:
    """Test Infrastructure DTOs"""
    
    def test_mr_metrics_response_creation(self):
        """Test MRMetricsResponse creation"""
        from src.modules.mr_analytics.infrastructure.query.dto import MRMetricsResponse
        
        data = {
            "mr_iid": 1,
            "title": "Test MR",
            "author": "author1",
            "created_at": "2024-01-01T10:00:00",
            "merged_at": "2024-01-02T14:00:00",
            "web_url": "https://gitlab.com/test/1",
            "additions": 100,
            "deletions": 50,
            "risk_score": "low"
        }
        
        response = MRMetricsResponse(**data)
        
        assert response.mr_iid == 1
        assert response.title == "Test MR"
        assert response.author == "author1"
        assert response.risk_score == "low"
    
    def test_mr_metrics_list_response_creation(self):
        """Test MRMetricsListResponse creation"""
        from src.modules.mr_analytics.infrastructure.query.dto import MRMetricsResponse, MRMetricsListResponse
        
        metrics_data = [
            {
                "mr_iid": 1,
                "title": "Test MR 1",
                "author": "author1",
                "risk_score": "low"
            },
            {
                "mr_iid": 2,
                "title": "Test MR 2", 
                "author": "author2",
                "risk_score": "medium"
            }
        ]
        
        metrics = [MRMetricsResponse(**data) for data in metrics_data]
        response = MRMetricsListResponse(data=metrics, total=2)
        
        assert len(response.data) == 2
        assert response.total == 2
        assert response.data[0].mr_iid == 1
        assert response.data[1].mr_iid == 2
    
    def test_reviewer_profile_dto_creation(self):
        """Test ReviewerProfile DTO creation"""
        from src.modules.mr_analytics.infrastructure.dto import ReviewerProfile
        
        data = {
            "name": "reviewer1",
            "mr_count": 50,
            "avg_review_time": 2.5,
            "recent_activity": 0.8,
            "workload_score": 0.6,
            "collaboration_index": 0.7
        }
        
        profile = ReviewerProfile(**data)
        
        assert profile.name == "reviewer1"
        assert profile.mr_count == 50
        assert profile.avg_review_time == 2.5
        assert profile.recent_activity == 0.8
        assert profile.workload_score == 0.6
        assert profile.collaboration_index == 0.7


class TestInfrastructureClients:
    """Test Infrastructure Clients"""
    
    @pytest.mark.asyncio
    async def test_gitlab_client_initialization(self):
        """Test GitLab client initialization"""
        # This would test the actual GitLab client if it exists
        # For now, we'll test the structure
        try:
            from src.modules.mr_analytics.infrastructure.clients.gitlab_client import GitLabClient
            
            client = GitLabClient(base_url="https://gitlab.com", token="test_token")
            
            assert client.base_url == "https://gitlab.com"
            assert client.token == "test_token"
        except ImportError:
            pytest.skip("GitLab client not implemented")
    
    @pytest.mark.asyncio
    async def test_analytics_service_client(self):
        """Test analytics service client"""
        # This would test the analytics service client if it exists
        try:
            from src.modules.mr_analytics.infrastructure.clients.analytics_client import AnalyticsClient
            
            client = AnalyticsClient(service_url="http://analytics-service")
            
            assert client.service_url == "http://analytics-service"
        except ImportError:
            pytest.skip("Analytics client not implemented")
