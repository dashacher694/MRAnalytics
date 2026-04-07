"""
Tests for SuggestReviewers UseCase
"""
from unittest.mock import AsyncMock, Mock, patch
import pytest

from src.modules.mr_analytics.usecase.suggest_reviewers.impl import SuggestReviewersUseCase
from src.modules.mr_analytics.usecase.suggest_reviewers.command import SuggestReviewersRequest, SuggestReviewersResponse
from src.modules.mr_analytics.infrastructure.dto import ReviewerSuggestion
from src.modules.mr_analytics.domain.aggregate.model import MRMetrics, RiskScore


@pytest.fixture
def mock_uow():
    """Mock Unit of Work"""
    uow = Mock()
    uow.metrics_repository = AsyncMock()
    return uow


@pytest.fixture
def usecase(mock_uow):
    """SuggestReviewers usecase instance"""
    return SuggestReviewersUseCase(mock_uow)


@pytest.fixture
def sample_metrics():
    """Sample MRMetrics data"""
    return [
        MRMetrics(
            mr_iid=1,
            title="Backend MR",
            author="author1",
            created_at="2024-01-01T10:00:00",
            merged_at="2024-01-02T14:00:00",
            web_url="https://gitlab.com/test/1",
            additions=100,
            deletions=50,
            suggested_reviewers=["reviewer1", "reviewer2"],
            risk_score=RiskScore.LOW
        ),
        MRMetrics(
            mr_iid=2,
            title="Frontend MR",
            author="author2",
            created_at="2024-01-03T10:00:00",
            merged_at="2024-01-04T14:00:00",
            web_url="https://gitlab.com/test/2",
            additions=200,
            deletions=100,
            suggested_reviewers=["reviewer2", "reviewer3"],
            risk_score=RiskScore.MEDIUM
        )
    ]


class TestSuggestReviewersUseCase:
    
    @pytest.mark.asyncio
    async def test_suggest_reviewers_success(self, usecase, mock_uow, sample_metrics):
        """Test successful reviewer suggestion"""
        # Arrange
        mr_iid = 1
        mock_uow.metrics_repository.get_by_iid.return_value = sample_metrics[0]
        request = SuggestReviewersRequest(mr_iid=mr_iid)
        
        with patch('src.modules.mr_analytics.application.analytics_services.ReviewerSuggestionService') as mock_service:
            mock_service.get_suggested_reviewers.return_value = [
                ReviewerSuggestion(reviewer="reviewer1", score=0.9, reasoning="Expert in backend"),
                ReviewerSuggestion(reviewer="reviewer2", score=0.8, reasoning="Available reviewer"),
                ReviewerSuggestion(reviewer="reviewer3", score=0.7, reasoning="Good response time")
            ]
            
            # Act
            result = await usecase.invoke(request)
            
            # Assert
            assert isinstance(result, SuggestReviewersResponse)
            assert result.mr_iid == mr_iid
            assert len(result.suggestions) == 3
            assert result.suggestions[0].reviewer == "reviewer1"
            assert result.suggestions[0].score == 0.9
            assert result.suggestions[1].reviewer == "reviewer2"
            assert result.suggestions[2].reviewer == "reviewer3"
            
            mock_uow.metrics_repository.get_by_iid.assert_called_once_with(mr_iid)
            mock_service.get_suggested_reviewers.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_suggest_reviewers_mr_not_found(self, usecase, mock_uow):
        """Test reviewer suggestion when MR not found"""
        # Arrange
        mr_iid = 999
        mock_uow.metrics_repository.get_by_iid.return_value = None
        request = SuggestReviewersRequest(mr_iid=mr_iid)
        
        # Act & Assert
        from src.modules.utils.errors import NotFoundError
        with pytest.raises(NotFoundError, match="MR with IID 999 not found"):
            await usecase.invoke(request)
    
    @pytest.mark.asyncio
    async def test_suggest_reviewers_empty_suggestions(self, usecase, mock_uow, sample_metrics):
        """Test reviewer suggestion when no suggestions available"""
        # Arrange
        mr_iid = 1
        mock_uow.metrics_repository.get_by_iid.return_value = sample_metrics[0]
        request = SuggestReviewersRequest(mr_iid=mr_iid)
        
        with patch('src.modules.mr_analytics.application.analytics_services.ReviewerSuggestionService') as mock_service:
            mock_service.get_suggested_reviewers.return_value = []
            
            # Act
            result = await usecase.invoke(request)
            
            # Assert
            assert isinstance(result, SuggestReviewersResponse)
            assert result.mr_iid == mr_iid
            assert len(result.suggestions) == 0
    
    @pytest.mark.asyncio
    async def test_suggest_reviewers_service_error(self, usecase, mock_uow, sample_metrics):
        """Test reviewer suggestion when service fails"""
        # Arrange
        mr_iid = 1
        mock_uow.metrics_repository.get_by_iid.return_value = sample_metrics[0]
        request = SuggestReviewersRequest(mr_iid=mr_iid)
        
        with patch('src.modules.mr_analytics.application.analytics_services.ReviewerSuggestionService') as mock_service:
            mock_service.get_suggested_reviewers.side_effect = Exception("Service failed")
            
            # Act & Assert
            with pytest.raises(Exception, match="Service failed"):
                await usecase.invoke(request)
    
    @pytest.mark.asyncio
    async def test_suggest_reviewers_response_structure(self, usecase, mock_uow, sample_metrics):
        """Test reviewer suggestion response structure"""
        # Arrange
        mr_iid = 1
        mock_uow.metrics_repository.get_by_iid.return_value = sample_metrics[0]
        request = SuggestReviewersRequest(mr_iid=mr_iid)
        
        with patch('src.modules.mr_analytics.application.analytics_services.ReviewerSuggestionService') as mock_service:
            mock_service.get_suggested_reviewers.return_value = [
                ReviewerSuggestion(reviewer="reviewer1", score=0.9, reasoning="Expert"),
                ReviewerSuggestion(reviewer="reviewer2", score=0.8, reasoning="Available")
            ]
            
            # Act
            result = await usecase.invoke(request)
            
            # Assert
            assert hasattr(result, 'mr_iid')
            assert hasattr(result, 'suggestions')
            assert isinstance(result.mr_iid, int)
            assert isinstance(result.suggestions, list)
            assert all(isinstance(s, ReviewerSuggestion) for s in result.suggestions)
            assert all(hasattr(s, 'reviewer') for s in result.suggestions)
            assert all(hasattr(s, 'score') for s in result.suggestions)
            assert all(hasattr(s, 'reasoning') for s in result.suggestions)
    
    @pytest.mark.asyncio
    async def test_suggest_reviewers_with_existing_suggestions(self, usecase, mock_uow, sample_metrics):
        """Test reviewer suggestion with existing suggestions in metrics"""
        # Arrange
        mr_iid = 1
        mock_uow.metrics_repository.get_by_iid.return_value = sample_metrics[0]  # Has suggested_reviewers
        request = SuggestReviewersRequest(mr_iid=mr_iid)
        
        with patch('src.modules.mr_analytics.application.analytics_services.ReviewerSuggestionService') as mock_service:
            mock_service.get_suggested_reviewers.return_value = [
                ReviewerSuggestion(reviewer="reviewer4", score=0.8, reasoning="New expert"),
                ReviewerSuggestion(reviewer="reviewer5", score=0.7, reasoning="Available")
            ]
            
            # Act
            result = await usecase.invoke(request)
            
            # Assert
            assert len(result.suggestions) == 2
            assert result.suggestions[0].reviewer == "reviewer4"
            assert result.suggestions[1].reviewer == "reviewer5"
            # Should return new suggestions, not existing ones
            assert not any(s.reviewer == "reviewer1" for s in result.suggestions)
    
    @pytest.mark.asyncio
    async def test_suggest_reviewers_different_mr_types(self, usecase, mock_uow, sample_metrics):
        """Test reviewer suggestion for different MR types"""
        # Test backend MR
        mock_uow.metrics_repository.get_by_iid.return_value = sample_metrics[0]
        request = SuggestReviewersRequest(mr_iid=1)
        
        with patch('src.modules.mr_analytics.application.analytics_services.ReviewerSuggestionService') as mock_service:
            mock_service.get_suggested_reviewers.return_value = [
                ReviewerSuggestion(reviewer="backend_reviewer1", score=0.9, reasoning="Backend expert"),
                ReviewerSuggestion(reviewer="backend_reviewer2", score=0.8, reasoning="Senior backend dev")
            ]
            
            result = await usecase.invoke(request)
            assert len(result.suggestions) == 2
            assert result.suggestions[0].reviewer == "backend_reviewer1"
            
        # Test frontend MR
        mock_uow.metrics_repository.get_by_iid.return_value = sample_metrics[1]
        request = SuggestReviewersRequest(mr_iid=2)
        
        with patch('src.modules.mr_analytics.application.analytics_services.ReviewerSuggestionService') as mock_service:
            mock_service.get_suggested_reviewers.return_value = [
                ReviewerSuggestion(reviewer="frontend_reviewer1", score=0.9, reasoning="Frontend expert"),
                ReviewerSuggestion(reviewer="frontend_reviewer2", score=0.8, reasoning="UI/UX specialist")
            ]
            
            result = await usecase.invoke(request)
            assert len(result.suggestions) == 2
            assert result.suggestions[0].reviewer == "frontend_reviewer1"
