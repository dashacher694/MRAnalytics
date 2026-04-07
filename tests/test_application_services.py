"""
Tests for Application Services
"""
from unittest.mock import Mock, patch
import pytest

from src.modules.mr_analytics.application.analytics_services import (
    BurnoutAnalyticsService,
    RiskPredictionService,
    AnomalyDetectionService,
    ReviewerProfile
)
from src.modules.mr_analytics.domain.aggregate.model import MRMetrics, RiskScore


class TestReviewerProfile:
    """Test ReviewerProfile value object"""
    
    def test_reviewer_profile_creation(self):
        """Test ReviewerProfile creation"""
        profile = ReviewerProfile(
            name="reviewer1",
            mr_count=50,
            avg_review_time=2.5,
            recent_activity=0.8,
            workload_score=0.6,
            collaboration_index=0.7
        )
        
        assert profile.name == "reviewer1"
        assert profile.mr_count == 50
        assert profile.avg_review_time == 2.5
        assert profile.recent_activity == 0.8
        assert profile.workload_score == 0.6
        assert profile.collaboration_index == 0.7
    
    def test_reviewer_profile_validation(self):
        """Test ReviewerProfile validation"""
        # Test valid values
        profile = ReviewerProfile(
            name="reviewer1",
            mr_count=0,  # Valid: can be zero
            avg_review_time=0.0,  # Valid: can be zero
            recent_activity=0.0,  # Valid: can be zero
            workload_score=0.0,  # Valid: can be zero
            collaboration_index=0.0  # Valid: can be zero
        )
        
        assert profile.mr_count == 0
        assert profile.avg_review_time == 0.0
        assert profile.recent_activity == 0.0
        assert profile.workload_score == 0.0
        assert profile.collaboration_index == 0.0
    
    def test_reviewer_profile_bounds(self):
        """Test ReviewerProfile bounds checking"""
        # Test upper bounds
        profile = ReviewerProfile(
            name="reviewer1",
            mr_count=1000,
            avg_review_time=100.0,
            recent_activity=1.0,
            workload_score=1.0,
            collaboration_index=1.0
        )
        
        assert profile.recent_activity <= 1.0
        assert profile.workload_score <= 1.0
        assert profile.collaboration_index <= 1.0


class TestBurnoutAnalyticsService:
    """Test BurnoutAnalyticsService"""
    
    def test_calculate_burnout_index_low(self):
        """Test burnout index calculation for low burnout"""
        profile = ReviewerProfile(
            name="reviewer1",
            mr_count=10,
            avg_review_time=1.0,
            recent_activity=0.9,
            workload_score=0.2,
            collaboration_index=0.8
        )
        
        burnout = BurnoutAnalyticsService.calculate_burnout_index(profile)
        
        assert 0.0 <= burnout <= 1.0
        assert burnout < 0.5  # Should be low burnout
    
    def test_calculate_burnout_index_high(self):
        """Test burnout index calculation for high burnout"""
        profile = ReviewerProfile(
            name="reviewer1",
            mr_count=100,
            avg_review_time=10.0,
            recent_activity=0.2,
            workload_score=0.9,
            collaboration_index=0.1
        )
        
        burnout = BurnoutAnalyticsService.calculate_burnout_index(profile)
        
        assert 0.0 <= burnout <= 1.0
        assert burnout > 0.7  # Should be high burnout
    
    def test_calculate_burnout_index_medium(self):
        """Test burnout index calculation for medium burnout"""
        profile = ReviewerProfile(
            name="reviewer1",
            mr_count=50,
            avg_review_time=3.0,
            recent_activity=0.5,
            workload_score=0.5,
            collaboration_index=0.5
        )
        
        burnout = BurnoutAnalyticsService.calculate_burnout_index(profile)
        
        assert 0.0 <= burnout <= 1.0
        assert 0.3 <= burnout <= 0.7  # Should be medium burnout
    
    def test_calculate_burnout_index_edge_cases(self):
        """Test burnout index calculation edge cases"""
        # Test zero workload
        profile_zero = ReviewerProfile(
            name="reviewer1",
            mr_count=0,
            avg_review_time=0.0,
            recent_activity=0.0,
            workload_score=0.0,
            collaboration_index=0.0
        )
        
        burnout_zero = BurnoutAnalyticsService.calculate_burnout_index(profile_zero)
        assert 0.0 <= burnout_zero <= 1.0
        
        # Test maximum workload
        profile_max = ReviewerProfile(
            name="reviewer1",
            mr_count=1000,
            avg_review_time=100.0,
            recent_activity=1.0,
            workload_score=1.0,
            collaboration_index=1.0
        )
        
        burnout_max = BurnoutAnalyticsService.calculate_burnout_index(profile_max)
        assert 0.0 <= burnout_max <= 1.0


class TestRiskPredictionService:
    """Test RiskPredictionService"""
    
    def test_predict_risk_low(self):
        """Test risk prediction for low risk MR"""
        metrics = MRMetrics(
            mr_iid=1,
            title="Small MR",
            author="author1",
            additions=50,
            deletions=25,
            review_rounds=1,
            comment_density=0.01,
            num_comments=1,
            num_approvals=2,
            author_mr_count=10
        )
        
        risk = RiskPredictionService.predict_risk(metrics)
        
        assert isinstance(risk, RiskScore)
        assert risk == RiskScore.LOW
    
    def test_predict_risk_high(self):
        """Test risk prediction for high risk MR"""
        metrics = MRMetrics(
            mr_iid=1,
            title="Large Complex MR",
            author="new_author",
            additions=1000,
            deletions=500,
            review_rounds=5,
            comment_density=0.1,
            num_comments=50,
            num_approvals=1,
            author_mr_count=1
        )
        
        risk = RiskPredictionService.predict_risk(metrics)
        
        assert isinstance(risk, RiskScore)
        assert risk == RiskScore.HIGH
    
    def test_predict_risk_medium(self):
        """Test risk prediction for medium risk MR"""
        metrics = MRMetrics(
            mr_iid=1,
            title="Medium MR",
            author="author1",
            additions=200,
            deletions=100,
            review_rounds=2,
            comment_density=0.03,
            num_comments=6,
            num_approvals=2,
            author_mr_count=20
        )
        
        risk = RiskPredictionService.predict_risk(metrics)
        
        assert isinstance(risk, RiskScore)
        assert risk == RiskScore.MEDIUM
    
    def test_predict_risk_considering_multiple_factors(self):
        """Test risk prediction considers multiple factors"""
        # High additions but low review rounds should be medium risk
        metrics = MRMetrics(
            mr_iid=1,
            title="Large but simple MR",
            author="experienced_author",
            additions=800,
            deletions=100,
            review_rounds=1,
            comment_density=0.01,
            num_comments=9,
            num_approvals=3,
            author_mr_count=100
        )
        
        risk = RiskPredictionService.predict_risk(metrics)
        
        assert isinstance(risk, RiskScore)
        # Should be medium or low due to experienced author and quick review
        assert risk in [RiskScore.LOW, RiskScore.MEDIUM]


class TestAnomalyDetectionService:
    """Test AnomalyDetectionService"""
    
    def test_find_anomalies_empty_list(self):
        """Test anomaly detection with empty metrics list"""
        metrics = []
        
        anomalies = AnomalyDetectionService.find_anomalies(metrics)
        
        assert anomalies == []
    
    def test_find_anomalies_single_metric(self):
        """Test anomaly detection with single metric"""
        metrics = [MRMetrics(mr_iid=1, title="Single MR", author="author1")]
        
        anomalies = AnomalyDetectionService.find_anomalies(metrics)
        
        assert len(anomalies) == 0  # Single item can't be anomaly
    
    def test_find_anomalies_normal_distribution(self):
        """Test anomaly detection with normal distribution"""
        metrics = [
            MRMetrics(mr_iid=i, title=f"MR {i}", author="author1", additions=100)
            for i in range(1, 11)  # 10 similar metrics
        ]
        
        anomalies = AnomalyDetectionService.find_anomalies(metrics)
        
        # Should have few or no anomalies in normal distribution
        assert len(anomalies) <= 2
    
    def test_find_anomalies_with_outliers(self):
        """Test anomaly detection with clear outliers"""
        metrics = [
            MRMetrics(mr_iid=i, title=f"MR {i}", author="author1", additions=100)
            for i in range(1, 9)  # 8 normal metrics
        ]
        # Add 2 clear outliers
        metrics.append(MRMetrics(mr_iid=9, title="Huge MR", author="author1", additions=5000))
        metrics.append(MRMetrics(mr_iid=10, title="Tiny MR", author="author1", additions=1))
        
        anomalies = AnomalyDetectionService.find_anomalies(metrics)
        
        # Should detect the outliers
        assert len(anomalies) >= 1
        
        # Check if outliers are detected
        anomaly_iids = [m.mr_iid for m in anomalies]
        assert 9 in anomaly_iids or 10 in anomaly_iids
    
    def test_find_anomalies_considers_multiple_fields(self):
        """Test anomaly detection considers multiple fields"""
        metrics = [
            MRMetrics(mr_iid=i, title=f"MR {i}", author="author1", additions=100, deletions=50)
            for i in range(1, 6)  # 5 normal metrics
        ]
        # Add metric with unusual pattern (high additions, low deletions)
        metrics.append(MRMetrics(
            mr_iid=6,
            title="Unusual MR",
            author="author1",
            additions=1000,
            deletions=5  # Very low deletions for high additions
        ))
        
        anomalies = AnomalyDetectionService.find_anomalies(metrics)
        
        # Should detect the unusual pattern
        anomaly_iids = [m.mr_iid for m in anomalies]
        assert 6 in anomaly_iids
    
    def test_find_anomalies_statistical_method(self):
        """Test anomaly detection uses statistical methods"""
        # Create metrics with clear statistical outliers
        import random
        random.seed(42)  # For reproducible results
        
        # Normal metrics around mean 100 with std 20
        normal_metrics = []
        for i in range(20):
            additions = int(random.gauss(100, 20))
            additions = max(50, min(150, additions))  # Clamp to reasonable range
            normal_metrics.append(MRMetrics(
                mr_iid=i+1,
                title=f"Normal MR {i+1}",
                author="author1",
                additions=additions
            ))
        
        # Add clear outliers
        normal_metrics.append(MRMetrics(mr_iid=21, title="Outlier 1", author="author1", additions=500))
        normal_metrics.append(MRMetrics(mr_iid=22, title="Outlier 2", author="author1", additions=10))
        
        anomalies = AnomalyDetectionService.find_anomalies(normal_metrics)
        
        # Should detect statistical outliers
        anomaly_iids = [m.mr_iid for m in anomalies]
        assert 21 in anomaly_iids or 22 in anomaly_iids


class TestAnalyticsServiceIntegration:
    """Test analytics services integration"""
    
    def test_burnout_and_risk_correlation(self):
        """Test correlation between burnout and risk prediction"""
        # Create a high-burnout reviewer profile
        high_burnout_profile = ReviewerProfile(
            name="burned_out_reviewer",
            mr_count=100,
            avg_review_time=8.0,
            recent_activity=0.1,
            workload_score=0.9,
            collaboration_index=0.2
        )
        
        burnout_score = BurnoutAnalyticsService.calculate_burnout_index(high_burnout_profile)
        
        # Create metrics for MR by this reviewer
        metrics = MRMetrics(
            mr_iid=1,
            title="MR by burned out reviewer",
            author="some_author",
            additions=200,
            deletions=100,
            review_rounds=4,  # High rounds due to slow review
            comment_density=0.08,
            num_comments=24,
            num_approvals=1,
            author_mr_count=5
        )
        
        risk_score = RiskPredictionService.predict_risk(metrics)
        
        # High burnout should correlate with higher risk
        assert burnout_score > 0.7
        assert risk_score in [RiskScore.MEDIUM, RiskScore.HIGH]
    
    def test_anomaly_detection_integration(self):
        """Test anomaly detection integration with other services"""
        # Create metrics with some anomalies
        metrics = [
            MRMetrics(mr_iid=i, title=f"MR {i}", author="author1", additions=100)
            for i in range(1, 8)
        ]
        metrics.append(MRMetrics(mr_iid=8, title="Anomaly MR", author="author1", additions=1000))
        
        # Detect anomalies
        anomalies = AnomalyDetectionService.find_anomalies(metrics)
        
        # Predict risk for all metrics
        risk_predictions = [RiskPredictionService.predict_risk(m) for m in metrics]
        
        # Anomalies should have different risk profile
        anomaly_iids = [m.mr_iid for m in anomalies]
        if 8 in anomaly_iids:
            anomaly_risk = risk_predictions[7]  # Index 7 for mr_iid 8
            # Anomaly should have higher risk
            assert anomaly_risk in [RiskScore.MEDIUM, RiskScore.HIGH]
