"""
Tests for API Endpoints
"""
from unittest.mock import AsyncMock, Mock, patch
import pytest
from fastapi.testclient import TestClient
import uuid

from src.modules.mr_analytics.usecase.get_metrics.api import router as get_metrics_router
from src.modules.mr_analytics.usecase.analyze_burnout.api import router as burnout_router
from src.modules.mr_analytics.usecase.predict_risk.api import router as predict_router
from src.modules.mr_analytics.usecase.get_metrics.command import GetMetricsRequest, GetMetricsResponse
from src.modules.mr_analytics.usecase.analyze_burnout.command import AnalyzeBurnoutRequest, BurnoutResponse
from src.modules.mr_analytics.usecase.predict_risk.command import PredictRiskResponse
from src.modules.mr_analytics.infrastructure.query.dto import MRMetricsResponse, MRMetricsListResponse


@pytest.fixture
def app():
    """Create FastAPI app for testing"""
    from fastapi import FastAPI
    app = FastAPI()
    app.include_router(get_metrics_router, prefix="/api/v1")
    app.include_router(burnout_router, prefix="/api/v1")
    app.include_router(predict_router, prefix="/api/v1")
    return app


@pytest.fixture
def client(app):
    """Test client"""
    return TestClient(app)


@pytest.fixture
def mock_get_metrics_uc():
    """Mock GetMetrics usecase"""
    return Mock()


@pytest.fixture
def mock_analyze_burnout_uc():
    """Mock AnalyzeBurnout usecase"""
    return Mock()


@pytest.fixture
def mock_predict_risk_uc():
    """Mock PredictRisk usecase"""
    return Mock()


class TestGetMetricsAPI:
    """Test GetMetrics API endpoint"""
    
    def test_get_metrics_success(self, client, mock_get_metrics_uc):
        """Test successful GET /metrics request"""
        # Arrange
        sample_metrics = [
            {
                "mr_iid": 1,
                "title": "Test MR",
                "author": "author1",
                "created_at": "2024-01-01T10:00:00",
                "merged_at": "2024-01-02T14:00:00",
                "web_url": "https://gitlab.com/test/1",
                "additions": 100,
                "deletions": 50,
                "time_to_merge": 28.0,
                "review_rounds": 2,
                "comment_density": 0.02,
                "formal_approval": 0,
                "response_time_hours": 2.0,
                "num_comments": 3,
                "num_approvals": 2,
                "risk_score": "low"
            }
        ]
        
        mock_response = GetMetricsResponse(metrics=sample_metrics, total=1)
        mock_get_metrics_uc.invoke = AsyncMock(return_value=mock_response)
        
        with patch('src.modules.mr_analytics.usecase.get_metrics.api.Depends') as mock_depends:
            mock_depends.return_value = mock_get_metrics_uc
            
            # Act
            response = client.get("/api/v1/metrics")
            
            # Assert
            assert response.status_code == 200
            data = response.json()
            assert "data" in data
            assert "total" in data
            assert data["total"] == 1
            assert len(data["data"]) == 1
            assert data["data"][0]["mr_iid"] == 1
    
    def test_get_metrics_with_filters(self, client, mock_get_metrics_uc):
        """Test GET /metrics with query parameters"""
        # Arrange
        mock_response = GetMetricsResponse(metrics=[], total=0)
        mock_get_metrics_uc.invoke = AsyncMock(return_value=mock_response)
        
        with patch('src.modules.mr_analytics.usecase.get_metrics.api.Depends') as mock_depends:
            mock_depends.return_value = mock_get_metrics_uc
            
            # Act
            response = client.get("/api/v1/metrics?mr_iid=123&author=testuser&days=7")
            
            # Assert
            assert response.status_code == 200
            
            # Verify the usecase was called with correct parameters
            call_args = mock_get_metrics_uc.invoke.call_args[0][0]
            assert isinstance(call_args, GetMetricsRequest)
            assert call_args.mr_iid == 123
            assert call_args.author == "testuser"
            assert call_args.days == 7
    
    def test_get_metrics_validation_error(self, client, mock_get_metrics_uc):
        """Test GET /metrics with invalid parameters"""
        # Act
        response = client.get("/api/v1/metrics?days=400")  # Invalid days > 365
        
        # Assert
        assert response.status_code == 422  # Validation error
    
    def test_get_metrics_not_found_error(self, client, mock_get_metrics_uc):
        """Test GET /metrics when metrics not found"""
        # Arrange
        from src.modules.utils.errors import NotFoundError
        mock_get_metrics_uc.invoke = AsyncMock(side_effect=NotFoundError("Metrics not found"))
        
        with patch('src.modules.mr_analytics.usecase.get_metrics.api.Depends') as mock_depends:
            mock_depends.return_value = mock_get_metrics_uc
            
            # Act
            response = client.get("/api/v1/metrics?mr_iid=999")
            
            # Assert
            assert response.status_code == 404
            data = response.json()
            assert "detail" in data
            assert "Metrics not found" in data["detail"]


class TestAnalyzeBurnoutAPI:
    """Test AnalyzeBurnout API endpoint"""
    
    def test_analyze_burnout_success(self, client, mock_analyze_burnout_uc):
        """Test successful POST /burnout-analysis request"""
        # Arrange
        request_data = {
            "team_profiles": [
                {
                    "name": "reviewer1",
                    "mr_count": 50,
                    "avg_review_time": 2.5,
                    "recent_activity": 0.8,
                    "workload_score": 0.6,
                    "collaboration_index": 0.7
                }
            ]
        }
        
        mock_response = BurnoutResponse(
            team_burnout_avg=0.65,
            high_risk_reviewers=[],
            burnout_scores={"reviewer1": 0.65}
        )
        mock_analyze_burnout_uc.invoke = AsyncMock(return_value=mock_response)
        
        with patch('src.modules.mr_analytics.usecase.analyze_burnout.api.Depends') as mock_depends:
            mock_depends.return_value = mock_analyze_burnout_uc
            
            # Act
            response = client.post("/api/v1/burnout-analysis", json=request_data)
            
            # Assert
            assert response.status_code == 200
            data = response.json()
            assert "team_burnout_avg" in data
            assert "high_risk_reviewers" in data
            assert "burnout_scores" in data
            assert data["team_burnout_avg"] == 0.65
            assert len(data["high_risk_reviewers"]) == 0
            assert data["burnout_scores"]["reviewer1"] == 0.65
    
    def test_analyze_burnout_invalid_request(self, client, mock_analyze_burnout_uc):
        """Test POST /burnout-analysis with invalid request"""
        # Arrange
        invalid_data = {
            "team_profiles": [
                {
                    "name": "reviewer1"
                    # Missing required fields
                }
            ]
        }
        
        with patch('src.modules.mr_analytics.usecase.analyze_burnout.api.Depends') as mock_depends:
            mock_depends.return_value = mock_analyze_burnout_uc
            
            # Act
            response = client.post("/api/v1/burnout-analysis", json=invalid_data)
            
            # Assert
            assert response.status_code == 422  # Validation error
    
    def test_analyze_burnout_empty_team(self, client, mock_analyze_burnout_uc):
        """Test POST /burnout-analysis with empty team"""
        # Arrange
        request_data = {"team_profiles": []}
        
        mock_response = BurnoutResponse(
            team_burnout_avg=0.0,
            high_risk_reviewers=[],
            burnout_scores={}
        )
        mock_analyze_burnout_uc.invoke = AsyncMock(return_value=mock_response)
        
        with patch('src.modules.mr_analytics.usecase.analyze_burnout.api.Depends') as mock_depends:
            mock_depends.return_value = mock_analyze_burnout_uc
            
            # Act
            response = client.post("/api/v1/burnout-analysis", json=request_data)
            
            # Assert
            assert response.status_code == 200
            data = response.json()
            assert data["team_burnout_avg"] == 0.0
            assert len(data["high_risk_reviewers"]) == 0
            assert len(data["burnout_scores"]) == 0
    
    def test_analyze_burnout_server_error(self, client, mock_analyze_burnout_uc):
        """Test POST /burnout-analysis when service fails"""
        # Arrange
        mock_analyze_burnout_uc.invoke = AsyncMock(side_effect=Exception("Service failed"))
        
        with patch('src.modules.mr_analytics.usecase.analyze_burnout.api.Depends') as mock_depends:
            mock_depends.return_value = mock_analyze_burnout_uc
            
            # Act
            response = client.post("/api/v1/burnout-analysis", json={"team_profiles": []})
            
            # Assert
            assert response.status_code == 500


class TestPredictRiskAPI:
    """Test PredictRisk API endpoint"""
    
    def test_predict_risk_success(self, client, mock_predict_risk_uc):
        """Test successful GET /risk-prediction request"""
        # Arrange
        mock_response = PredictRiskResponse(
            total_analyzed=10,
            high_risk_count=2,
            medium_risk_count=3,
            low_risk_count=5,
            anomalies_count=1,
            risk_distribution={"high": 2, "medium": 3, "low": 5}
        )
        mock_predict_risk_uc.invoke = AsyncMock(return_value=mock_response)
        
        with patch('src.modules.mr_analytics.usecase.predict_risk.api.Depends') as mock_depends:
            mock_depends.return_value = mock_predict_risk_uc
            
            # Act
            response = client.get("/api/v1/risk-prediction")
            
            # Assert
            assert response.status_code == 200
            data = response.json()
            assert "total_analyzed" in data
            assert "high_risk_count" in data
            assert "medium_risk_count" in data
            assert "low_risk_count" in data
            assert "anomalies_count" in data
            assert "risk_distribution" in data
            assert data["total_analyzed"] == 10
            assert data["high_risk_count"] == 2
            assert data["medium_risk_count"] == 3
            assert data["low_risk_count"] == 5
            assert data["anomalies_count"] == 1
            assert data["risk_distribution"] == {"high": 2, "medium": 3, "low": 5}
    
    def test_predict_risk_with_days_parameter(self, client, mock_predict_risk_uc):
        """Test GET /risk-prediction with days parameter"""
        # Arrange
        mock_response = PredictRiskResponse(
            total_analyzed=5,
            high_risk_count=1,
            medium_risk_count=2,
            low_risk_count=2,
            anomalies_count=0,
            risk_distribution={"high": 1, "medium": 2, "low": 2}
        )
        mock_predict_risk_uc.invoke = AsyncMock(return_value=mock_response)
        
        with patch('src.modules.mr_analytics.usecase.predict_risk.api.Depends') as mock_depends:
            mock_depends.return_value = mock_predict_risk_uc
            
            # Act
            response = client.get("/api/v1/risk-prediction?days=7")
            
            # Assert
            assert response.status_code == 200
            
            # Verify the usecase was called with correct days parameter
            mock_predict_risk_uc.invoke.assert_called_once_with(7)
    
    def test_predict_risk_invalid_days(self, client, mock_predict_risk_uc):
        """Test GET /risk-prediction with invalid days parameter"""
        # Act
        response = client.get("/api/v1/risk-prediction?days=400")  # Invalid days > 365
        
        # Assert
        assert response.status_code == 422  # Validation error
    
    def test_predict_risk_no_metrics_found(self, client, mock_predict_risk_uc):
        """Test GET /risk-prediction when no metrics found"""
        # Arrange
        from src.modules.utils.errors import NotFoundError
        mock_predict_risk_uc.invoke = AsyncMock(side_effect=NotFoundError("No metrics found"))
        
        with patch('src.modules.mr_analytics.usecase.predict_risk.api.Depends') as mock_depends:
            mock_depends.return_value = mock_predict_risk_uc
            
            # Act
            response = client.get("/api/v1/risk-prediction?days=1")
            
            # Assert
            assert response.status_code == 404
            data = response.json()
            assert "detail" in data
            assert "No metrics found" in data["detail"]


class TestAPIIntegration:
    """Test API integration scenarios"""
    
    def test_api_response_format_consistency(self, client, mock_get_metrics_uc, mock_analyze_burnout_uc, mock_predict_risk_uc):
        """Test that all APIs return consistent response format"""
        # Arrange
        mock_metrics_response = GetMetricsResponse(metrics=[], total=0)
        mock_burnout_response = BurnoutResponse(
            team_burnout_avg=0.0,
            high_risk_reviewers=[],
            burnout_scores={}
        )
        mock_risk_response = PredictRiskResponse(
            total_analyzed=0,
            high_risk_count=0,
            medium_risk_count=0,
            low_risk_count=0,
            anomalies_count=0,
            risk_distribution={"high": 0, "medium": 0, "low": 0}
        )
        
        mock_get_metrics_uc.invoke = AsyncMock(return_value=mock_metrics_response)
        mock_analyze_burnout_uc.invoke = AsyncMock(return_value=mock_burnout_response)
        mock_predict_risk_uc.invoke = AsyncMock(return_value=mock_risk_response)
        
        with patch('src.modules.mr_analytics.usecase.get_metrics.api.Depends') as mock_depends1, \
             patch('src.modules.mr_analytics.usecase.analyze_burnout.api.Depends') as mock_depends2, \
             patch('src.modules.mr_analytics.usecase.predict_risk.api.Depends') as mock_depends3:
            
            mock_depends1.return_value = mock_get_metrics_uc
            mock_depends2.return_value = mock_analyze_burnout_uc
            mock_depends3.return_value = mock_predict_risk_uc
            
            # Act
            metrics_response = client.get("/api/v1/metrics")
            burnout_response = client.post("/api/v1/burnout-analysis", json={"team_profiles": []})
            risk_response = client.get("/api/v1/risk-prediction")
            
            # Assert
            assert metrics_response.status_code == 200
            assert burnout_response.status_code == 200
            assert risk_response.status_code == 200
            
            # All responses should be JSON
            assert metrics_response.headers["content-type"] == "application/json"
            assert burnout_response.headers["content-type"] == "application/json"
            assert risk_response.headers["content-type"] == "application/json"
