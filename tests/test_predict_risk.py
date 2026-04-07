"""
Tests for PredictRisk UseCase
"""
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, Mock, patch
import pytest

from src.modules.mr_analytics.usecase.predict_risk.impl import PredictRiskUseCase
from src.modules.mr_analytics.usecase.predict_risk.command import PredictRiskResponse
from src.modules.mr_analytics.domain.aggregate.model import MRMetrics, RiskScore
from src.modules.mr_analytics.application.analytics_services import RiskPredictionService, AnomalyDetectionService


@pytest.fixture
def mock_uow():
    """Mock Unit of Work"""
    uow = Mock()
    uow.metrics_repository = AsyncMock()
    return uow


@pytest.fixture
def usecase(mock_uow):
    """PredictRisk usecase instance"""
    return PredictRiskUseCase(mock_uow)


@pytest.fixture
def sample_metrics():
    """Sample MRMetrics data"""
    return [
        MRMetrics(
            mr_iid=1,
            title="Low Risk MR",
            author="author1",
            created_at=datetime(2024, 1, 1),
            merged_at=datetime(2024, 1, 2),
            web_url="https://gitlab.com/test/1",
            additions=50,
            deletions=25,
            risk_score=RiskScore.LOW
        ),
        MRMetrics(
            mr_iid=2,
            title="Medium Risk MR",
            author="author2",
            created_at=datetime(2024, 1, 3),
            merged_at=datetime(2024, 1, 4),
            web_url="https://gitlab.com/test/2",
            additions=150,
            deletions=75,
            risk_score=RiskScore.MEDIUM
        ),
        MRMetrics(
            mr_iid=3,
            title="High Risk MR",
            author="author3",
            created_at=datetime(2024, 1, 5),
            merged_at=datetime(2024, 1, 6),
            web_url="https://gitlab.com/test/3",
            additions=300,
            deletions=150,
            risk_score=RiskScore.HIGH
        ),
        MRMetrics(
            mr_iid=4,
            title="Anomalous MR",
            author="author4",
            created_at=datetime(2024, 1, 7),
            merged_at=datetime(2024, 1, 8),
            web_url="https://gitlab.com/test/4",
            additions=500,
            deletions=250,
            risk_score=RiskScore.MEDIUM,
            is_anomaly=False
        )
    ]


class TestPredictRiskUseCase:
    
    @pytest.mark.asyncio
    async def test_predict_risk_success(self, usecase, mock_uow, sample_metrics):
        """Test successful risk prediction"""
        # Arrange
        days = 30
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        mock_uow.metrics_repository.get_by_date_range.return_value = sample_metrics
        
        with patch.object(RiskPredictionService, 'predict_risk') as mock_predict, \
             patch.object(AnomalyDetectionService, 'find_anomalies') as mock_anomalies:
            
            mock_predict.side_effect = [RiskScore.LOW, RiskScore.MEDIUM, RiskScore.HIGH, RiskScore.MEDIUM]
            mock_anomalies.return_value = [sample_metrics[3]]  # Last metric is anomaly
            
            # Act
            result = await usecase.invoke(days)
            
            # Assert
            assert isinstance(result, PredictRiskResponse)
            assert result.total_analyzed == 4
            assert result.high_risk_count == 1
            assert result.medium_risk_count == 2
            assert result.low_risk_count == 1
            assert result.anomalies_count == 1
            
            # Verify risk distribution
            expected_dist = {"high": 1, "medium": 2, "low": 1}
            assert result.risk_distribution == expected_dist
            
            # Verify service calls
            assert mock_predict.call_count == 4
            assert mock_anomalies.call_count == 1
            mock_uow.metrics_repository.get_by_date_range.assert_called_once_with(start_date, end_date)
    
    @pytest.mark.asyncio
    async def test_predict_risk_empty_metrics(self, usecase, mock_uow):
        """Test risk prediction with no metrics"""
        # Arrange
        days = 30
        mock_uow.metrics_repository.get_by_date_range.return_value = []
        
        # Act
        result = await usecase.invoke(days)
        
        # Assert
        assert result.total_analyzed == 0
        assert result.high_risk_count == 0
        assert result.medium_risk_count == 0
        assert result.low_risk_count == 0
        assert result.anomalies_count == 0
        assert result.risk_distribution == {"high": 0, "medium": 0, "low": 0}
    
    @pytest.mark.asyncio
    async def test_predict_risk_all_high_risk(self, usecase, mock_uow, sample_metrics):
        """Test risk prediction when all metrics are high risk"""
        # Arrange
        days = 30
        mock_uow.metrics_repository.get_by_date_range.return_value = sample_metrics
        
        with patch.object(RiskPredictionService, 'predict_risk') as mock_predict, \
             patch.object(AnomalyDetectionService, 'find_anomalies') as mock_anomalies:
            
            mock_predict.return_value = RiskScore.HIGH
            mock_anomalies.return_value = []
            
            # Act
            result = await usecase.invoke(days)
            
            # Assert
            assert result.total_analyzed == 4
            assert result.high_risk_count == 4
            assert result.medium_risk_count == 0
            assert result.low_risk_count == 0
            assert result.risk_distribution == {"high": 4, "medium": 0, "low": 0}
    
    @pytest.mark.asyncio
    async def test_predict_risk_multiple_anomalies(self, usecase, mock_uow, sample_metrics):
        """Test risk prediction with multiple anomalies"""
        # Arrange
        days = 30
        mock_uow.metrics_repository.get_by_date_range.return_value = sample_metrics
        
        with patch.object(RiskPredictionService, 'predict_risk') as mock_predict, \
             patch.object(AnomalyDetectionService, 'find_anomalies') as mock_anomalies:
            
            mock_predict.return_value = RiskScore.LOW
            mock_anomalies.return_value = sample_metrics[:2]  # First two metrics are anomalies
            
            # Act
            result = await usecase.invoke(days)
            
            # Assert
            assert result.total_analyzed == 4
            assert result.anomalies_count == 2
            assert result.high_risk_count == 0
            assert result.medium_risk_count == 0
            assert result.low_risk_count == 4
            
            # Verify anomalies are marked
            assert sample_metrics[0].is_anomaly is True
            assert sample_metrics[1].is_anomaly is True
            assert sample_metrics[2].is_anomaly is False
            assert sample_metrics[3].is_anomaly is False
    
    @pytest.mark.asyncio
    async def test_predict_risk_default_days(self, usecase, mock_uow, sample_metrics):
        """Test risk prediction with default days parameter"""
        # Arrange
        mock_uow.metrics_repository.get_by_date_range.return_value = sample_metrics
        
        with patch.object(RiskPredictionService, 'predict_risk') as mock_predict, \
             patch.object(AnomalyDetectionService, 'find_anomalies') as mock_anomalies:
            
            mock_predict.return_value = RiskScore.LOW
            mock_anomalies.return_value = []
            
            # Act (no days parameter, should default to 30)
            result = await usecase.invoke()
            
            # Assert
            assert result.total_analyzed == 4
            # Verify the call was made with 30 days (default)
            call_args = mock_uow.metrics_repository.get_by_date_range.call_args[0]
            end_date = call_args[1]
            start_date = call_args[0]
            expected_start = end_date - timedelta(days=30)
            assert abs((start_date - expected_start).total_seconds()) < 1  # Allow 1 second tolerance
    
    @pytest.mark.asyncio
    async def test_predict_risk_custom_days(self, usecase, mock_uow, sample_metrics):
        """Test risk prediction with custom days parameter"""
        # Arrange
        days = 7
        mock_uow.metrics_repository.get_by_date_range.return_value = sample_metrics
        
        with patch.object(RiskPredictionService, 'predict_risk') as mock_predict, \
             patch.object(AnomalyDetectionService, 'find_anomalies') as mock_anomalies:
            
            mock_predict.return_value = RiskScore.LOW
            mock_anomalies.return_value = []
            
            # Act
            result = await usecase.invoke(days)
            
            # Assert
            assert result.total_analyzed == 4
            # Verify the call was made with custom days
            call_args = mock_uow.metrics_repository.get_by_date_range.call_args[0]
            end_date = call_args[1]
            start_date = call_args[0]
            expected_start = end_date - timedelta(days=7)
            assert abs((start_date - expected_start).total_seconds()) < 1
    
    @pytest.mark.asyncio
    async def test_predict_risk_score_assignment(self, usecase, mock_uow, sample_metrics):
        """Test that risk scores are properly assigned to metrics"""
        # Arrange
        days = 30
        mock_uow.metrics_repository.get_by_date_range.return_value = sample_metrics
        
        with patch.object(RiskPredictionService, 'predict_risk') as mock_predict, \
             patch.object(AnomalyDetectionService, 'find_anomalies') as mock_anomalies:
            
            predicted_scores = [RiskScore.LOW, RiskScore.HIGH, RiskScore.MEDIUM, RiskScore.LOW]
            mock_predict.side_effect = predicted_scores
            mock_anomalies.return_value = []
            
            # Act
            await usecase.invoke(days)
            
            # Assert
            for i, metric in enumerate(sample_metrics):
                assert metric.risk_score == predicted_scores[i]
    
    @pytest.mark.asyncio
    async def test_predict_risk_response_structure(self, usecase, mock_uow, sample_metrics):
        """Test response structure and types"""
        # Arrange
        days = 30
        mock_uow.metrics_repository.get_by_date_range.return_value = sample_metrics
        
        with patch.object(RiskPredictionService, 'predict_risk') as mock_predict, \
             patch.object(AnomalyDetectionService, 'find_anomalies') as mock_anomalies:
            
            mock_predict.return_value = RiskScore.LOW
            mock_anomalies.return_value = []
            
            # Act
            result = await usecase.invoke(days)
            
            # Assert
            assert isinstance(result.total_analyzed, int)
            assert isinstance(result.high_risk_count, int)
            assert isinstance(result.medium_risk_count, int)
            assert isinstance(result.low_risk_count, int)
            assert isinstance(result.anomalies_count, int)
            assert isinstance(result.risk_distribution, dict)
            
            # Check risk distribution structure
            assert "high" in result.risk_distribution
            assert "medium" in result.risk_distribution
            assert "low" in result.risk_distribution
            assert all(isinstance(v, int) for v in result.risk_distribution.values())
            
            # Verify counts match distribution
            assert result.risk_distribution["high"] == result.high_risk_count
            assert result.risk_distribution["medium"] == result.medium_risk_count
            assert result.risk_distribution["low"] == result.low_risk_count
