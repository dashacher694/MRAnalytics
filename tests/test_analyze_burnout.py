"""
Tests for AnalyzeBurnout UseCase
"""
from unittest.mock import AsyncMock, Mock
import pytest

from src.modules.mr_analytics.usecase.analyze_burnout.impl import AnalyzeBurnoutUseCase
from src.modules.mr_analytics.usecase.analyze_burnout.command import AnalyzeBurnoutRequest, BurnoutResponse
from src.modules.mr_analytics.application.analytics_services import BurnoutAnalyticsService, ReviewerProfile


@pytest.fixture
def mock_uow():
    """Mock Unit of Work"""
    uow = Mock()
    return uow


@pytest.fixture
def usecase(mock_uow):
    """AnalyzeBurnout usecase instance"""
    return AnalyzeBurnoutUseCase(mock_uow)


@pytest.fixture
def sample_team_profiles():
    """Sample team profile data"""
    return [
        {
            "name": "reviewer1",
            "mr_count": 50,
            "avg_review_time": 2.5,
            "recent_activity": 0.8,
            "workload_score": 0.6,
            "collaboration_index": 0.7
        },
        {
            "name": "reviewer2", 
            "mr_count": 30,
            "avg_review_time": 4.0,
            "recent_activity": 0.4,
            "workload_score": 0.9,
            "collaboration_index": 0.5
        },
        {
            "name": "reviewer3",
            "mr_count": 80,
            "avg_review_time": 1.0,
            "recent_activity": 0.9,
            "workload_score": 0.8,
            "collaboration_index": 0.9
        }
    ]


class TestAnalyzeBurnoutUseCase:
    
    @pytest.mark.asyncio
    async def test_analyze_burnout_success(self, usecase, sample_team_profiles):
        """Test successful burnout analysis"""
        # Arrange
        request = AnalyzeBurnoutRequest(team_profiles=sample_team_profiles)
        
        # Act
        result = await usecase.invoke(request)
        
        # Assert
        assert isinstance(result, BurnoutResponse)
        assert hasattr(result, 'team_burnout_avg')
        assert hasattr(result, 'high_risk_reviewers')
        assert hasattr(result, 'burnout_scores')
        
        # Verify structure
        assert isinstance(result.team_burnout_avg, float)
        assert isinstance(result.high_risk_reviewers, list)
        assert isinstance(result.burnout_scores, dict)
        
        # Verify all reviewers have scores
        assert len(result.burnout_scores) == 3
        for profile in sample_team_profiles:
            assert profile["name"] in result.burnout_scores
    
    @pytest.mark.asyncio
    async def test_analyze_burnout_high_risk_detection(self, usecase, sample_team_profiles, mocker):
        """Test high risk reviewers detection"""
        # Arrange
        # Mock BurnoutAnalyticsService to return predictable scores
        mock_calculate = mocker.patch.object(
            BurnoutAnalyticsService, 
            'calculate_burnout_index',
            side_effect=[0.9, 0.3, 0.85]  # reviewer1: high, reviewer2: low, reviewer3: high
        )
        request = AnalyzeBurnoutRequest(team_profiles=sample_team_profiles)
        
        # Act
        result = await usecase.invoke(request)
        
        # Assert
        assert len(result.high_risk_reviewers) == 2
        assert "reviewer1" in result.high_risk_reviewers
        assert "reviewer3" in result.high_risk_reviewers
        assert "reviewer2" not in result.high_risk_reviewers
        
        # Verify burnout scores
        assert result.burnout_scores["reviewer1"] == 0.9
        assert result.burnout_scores["reviewer2"] == 0.3
        assert result.burnout_scores["reviewer3"] == 0.85
    
    @pytest.mark.asyncio
    async def test_analyze_burnout_no_high_risk(self, usecase, sample_team_profiles, mocker):
        """Test when no reviewers have high burnout"""
        # Arrange
        mock_calculate = mocker.patch.object(
            BurnoutAnalyticsService,
            'calculate_burnout_index', 
            side_effect=[0.3, 0.4, 0.2]  # All low burnout
        )
        request = AnalyzeBurnoutRequest(team_profiles=sample_team_profiles)
        
        # Act
        result = await usecase.invoke(request)
        
        # Assert
        assert len(result.high_risk_reviewers) == 0
        assert result.team_burnout_avg == pytest.approx(0.3)  # (0.3 + 0.4 + 0.2) / 3
    
    @pytest.mark.asyncio
    async def test_analyze_burnout_empty_team(self, usecase):
        """Test burnout analysis with empty team"""
        # Arrange
        request = AnalyzeBurnoutRequest(team_profiles=[])
        
        # Act
        result = await usecase.invoke(request)
        
        # Assert
        assert result.team_burnout_avg == 0.0
        assert len(result.high_risk_reviewers) == 0
        assert len(result.burnout_scores) == 0
    
    @pytest.mark.asyncio
    async def test_analyze_burnout_single_reviewer(self, usecase, mocker):
        """Test burnout analysis with single reviewer"""
        # Arrange
        single_profile = [{
            "name": "single_reviewer",
            "mr_count": 25,
            "avg_review_time": 3.0,
            "recent_activity": 0.6,
            "workload_score": 0.7,
            "collaboration_index": 0.8
        }]
        mock_calculate = mocker.patch.object(
            BurnoutAnalyticsService,
            'calculate_burnout_index',
            return_value=0.5
        )
        request = AnalyzeBurnoutRequest(team_profiles=single_profile)
        
        # Act
        result = await usecase.invoke(request)
        
        # Assert
        assert len(result.burnout_scores) == 1
        assert result.burnout_scores["single_reviewer"] == 0.5
        assert result.team_burnout_avg == 0.5
    
    @pytest.mark.asyncio
    async def test_analyze_burnout_profile_conversion(self, usecase, sample_team_profiles, mocker):
        """Test that profile data is correctly converted to ReviewerProfile objects"""
        # Arrange
        mock_calculate = mocker.patch.object(
            BurnoutAnalyticsService,
            'calculate_burnout_index',
            return_value=0.4
        )
        request = AnalyzeBurnoutRequest(team_profiles=sample_team_profiles)
        
        # Act
        await usecase.invoke(request)
        
        # Assert
        # Verify calculate_burnout_index was called with ReviewerProfile objects
        assert mock_calculate.call_count == 3
        for call in mock_calculate.call_args_list:
            profile_arg = call[0][0]  # First argument of each call
            assert isinstance(profile_arg, ReviewerProfile)
    
    @pytest.mark.asyncio
    async def test_analyze_burnout_average_calculation(self, usecase, sample_team_profiles, mocker):
        """Test team average burnout calculation"""
        # Arrange
        scores = [0.2, 0.6, 0.8]
        mock_calculate = mocker.patch.object(
            BurnoutAnalyticsService,
            'calculate_burnout_index',
            side_effect=scores
        )
        request = AnalyzeBurnoutRequest(team_profiles=sample_team_profiles)
        
        # Act
        result = await usecase.invoke(request)
        
        # Assert
        expected_avg = sum(scores) / len(scores)
        assert result.team_burnout_avg == pytest.approx(expected_avg)
    
    @pytest.mark.asyncio
    async def test_analyze_burnout_response_structure(self, usecase, sample_team_profiles):
        """Test response structure and types"""
        # Arrange
        request = AnalyzeBurnoutRequest(team_profiles=sample_team_profiles)
        
        # Act
        result = await usecase.invoke(request)
        
        # Assert
        assert isinstance(result.team_burnout_avg, float)
        assert isinstance(result.high_risk_reviewers, list)
        assert isinstance(result.burnout_scores, dict)
        
        # Check high_risk_reviewers contains strings
        for reviewer in result.high_risk_reviewers:
            assert isinstance(reviewer, str)
        
        # Check burnout_scores keys and values
        for reviewer, score in result.burnout_scores.items():
            assert isinstance(reviewer, str)
            assert isinstance(score, float)
            assert 0 <= score <= 1  # Burnout scores should be between 0 and 1
