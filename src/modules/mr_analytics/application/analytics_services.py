from typing import List, Dict, Any
from datetime import datetime
from dataclasses import dataclass

from src.modules.mr_analytics.domain.aggregate.model import MRMetrics
from src.modules.mr_analytics.domain.enums import RiskScore
from src.modules.mr_analytics.domain.value_objects import Comment, Approval
from src.modules.mr_analytics.infrastructure.dto import ReviewerProfile
from src.modules.mr_analytics.domain.constants import RiskThresholds, ReviewerScoring, BurnoutThresholds


class RiskPredictionService:
    
    @staticmethod
    def predict_risk(mr: MRMetrics) -> RiskScore:
        risk = 0
        
        if mr.additions + mr.deletions > RiskThresholds.LINES_CHANGED_THRESHOLD:
            risk += 1
        
        if mr.comment_density > RiskThresholds.COMMENT_DENSITY_THRESHOLD:
            risk += 1
        
        if mr.response_time_hours and mr.response_time_hours > RiskThresholds.RESPONSE_TIME_THRESHOLD:
            risk += 1
        
        if mr.review_rounds > RiskThresholds.REVIEW_ROUNDS_THRESHOLD:
            risk += 1
        
        if risk >= RiskThresholds.HIGH_RISK_THRESHOLD:
            return RiskScore.HIGH
        elif risk >= RiskThresholds.MEDIUM_RISK_THRESHOLD:
            return RiskScore.MEDIUM
        else:
            return RiskScore.LOW


class ReviewerRecommendationService:
    
    @staticmethod
    def suggest_reviewers(mr: MRMetrics, team_profiles: List[ReviewerProfile]) -> List:
        suggestions = []
        
        for reviewer in team_profiles:
            score = 0.0
            reasoning_parts = []
            
            if mr.additions + mr.deletions > 0:
                expertise_match = ReviewerScoring.EXPERTISE_MATCH
                score += expertise_match * ReviewerScoring.EXPERTISE_WEIGHT
                reasoning_parts.append(f"file expertise")
            
            if reviewer.avg_response_time_hours > 0:
                response_score = max(0, (ReviewerScoring.RESPONSE_TIME_HOURS - min(reviewer.avg_response_time_hours, ReviewerScoring.RESPONSE_TIME_HOURS)) / ReviewerScoring.RESPONSE_TIME_HOURS) * ReviewerScoring.RESPONSE_TIME_WEIGHT
                score += response_score
                reasoning_parts.append(f"fast response")
            
            score += reviewer.quality_score * ReviewerScoring.QUALITY_WEIGHT
            reasoning_parts.append(f"quality")
            
            workload_score = max(0, (ReviewerScoring.WORKLOAD_MAX_REVIEWS - min(reviewer.open_reviews_count, ReviewerScoring.WORKLOAD_MAX_REVIEWS)) / ReviewerScoring.WORKLOAD_MAX_REVIEWS) * ReviewerScoring.WORKLOAD_WEIGHT
            score += workload_score
            reasoning_parts.append(f"available")
            
            suggestions.append({
                "reviewer": reviewer.name,
                "score": score,
                "reasoning": ", ".join(reasoning_parts)
            })
        
        return sorted(suggestions, key=lambda x: x["score"], reverse=True)[:ReviewerScoring.TOP_REVIEWERS_LIMIT]


class BurnoutAnalyticsService:
    
    @staticmethod
    def calculate_burnout_index(reviewer: ReviewerProfile) -> float:
        factors = []
        
        active_mrs = reviewer.pending_reviews_count
        factors.append(min(active_mrs / BurnoutThresholds.MAX_ACTIVE_MRS, 1.0))
        
        if reviewer.prev_week_avg_response_time > 0:
            slowdown = max(0, (reviewer.last_week_avg_response_time - reviewer.prev_week_avg_response_time) / reviewer.prev_week_avg_response_time)
            factors.append(min(slowdown, 1.0))
        
        if reviewer.prev_week_avg_comment_length > 0:
            shortening = max(0, (reviewer.prev_week_avg_comment_length - reviewer.last_week_avg_comment_length) / reviewer.prev_week_avg_comment_length)
            factors.append(shortening)
        
        return sum(factors) / len(factors) if factors else 0.0


class AnomalyDetectionService:
    
    @staticmethod
    def find_anomalies(mrs: List[MRMetrics]) -> List[MRMetrics]:
        anomalies = []
        
        all_times = [m.time_to_merge for m in mrs if m.time_to_merge]
        all_densities = [m.comment_density for m in mrs]
        all_rounds = [m.review_rounds for m in mrs]
        
        if not all_times or not all_densities or not all_rounds:
            return anomalies
        
        time_mean = sum(all_times) / len(all_times)
        time_std = (sum((x - time_mean) ** 2 for x in all_times) / len(all_times)) ** 0.5
        time_threshold = time_mean + BurnoutThresholds.ANOMALY_STD_DEVIATIONS * time_std
        
        density_mean = sum(all_densities) / len(all_densities)
        density_std = (sum((x - density_mean) ** 2 for x in all_densities) / len(all_densities)) ** 0.5
        density_threshold = density_mean + BurnoutThresholds.ANOMALY_STD_DEVIATIONS * density_std
        
        rounds_mean = sum(all_rounds) / len(all_rounds)
        rounds_std = (sum((x - rounds_mean) ** 2 for x in all_rounds) / len(all_rounds)) ** 0.5
        rounds_threshold = rounds_mean + BurnoutThresholds.ANOMALY_STD_DEVIATIONS * rounds_std
        
        for mr in mrs:
            is_anomaly = False
            reasons = []
            
            if mr.time_to_merge and mr.time_to_merge > time_threshold:
                is_anomaly = True
                reasons.append("unusually long merge time")
            
            if mr.comment_density > density_threshold:
                is_anomaly = True
                reasons.append("high comment density")
            
            if mr.review_rounds > rounds_threshold:
                is_anomaly = True
                reasons.append("many review rounds")
            
            if is_anomaly:
                mr.is_anomaly = True
                anomalies.append(mr)
        
        return anomalies
