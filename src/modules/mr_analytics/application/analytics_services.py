"""
Advanced analytics services for MR analysis
"""
from typing import List, Dict, Any
from datetime import datetime
from dataclasses import dataclass

from src.modules.mr_analytics.domain.aggregate.model import MRMetrics, RiskScore
from src.modules.mr_analytics.domain.value_objects import Comment, Approval
from src.modules.mr_analytics.infrastructure.dto import ReviewerProfile


class RiskPredictionService:
    
    @staticmethod
    def predict_risk(mr: MRMetrics) -> RiskScore:
        risk = 0
        
        if mr.additions + mr.deletions > 1000:
            risk += 1
        
        if mr.comment_density > 0.1:
            risk += 1
        
        if mr.response_time_hours and mr.response_time_hours > 24:
            risk += 1
        
        if mr.review_rounds > 5:
            risk += 1
        
        if risk >= 3:
            return RiskScore.HIGH
        elif risk >= 2:
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
                expertise_match = 0.5
                score += expertise_match * 10
                reasoning_parts.append(f"file expertise")
            
            if reviewer.avg_response_time_hours > 0:
                response_score = max(0, (24 - min(reviewer.avg_response_time_hours, 24)) / 24) * 5
                score += response_score
                reasoning_parts.append(f"fast response")
            
            score += reviewer.quality_score * 5
            reasoning_parts.append(f"quality")
            
            workload_score = max(0, (10 - min(reviewer.open_reviews_count, 10)) / 10) * 3
            score += workload_score
            reasoning_parts.append(f"available")
            
            suggestions.append({
                "reviewer": reviewer.name,
                "score": score,
                "reasoning": ", ".join(reasoning_parts)
            })
        
        return sorted(suggestions, key=lambda x: x["score"], reverse=True)[:3]


class BurnoutAnalyticsService:
    
    @staticmethod
    def calculate_burnout_index(reviewer: ReviewerProfile) -> float:
        factors = []
        
        active_mrs = reviewer.pending_reviews_count
        factors.append(min(active_mrs / 10, 1.0))
        
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
        time_threshold = time_mean + 2 * time_std
        
        density_mean = sum(all_densities) / len(all_densities)
        density_std = (sum((x - density_mean) ** 2 for x in all_densities) / len(all_densities)) ** 0.5
        density_threshold = density_mean + 2 * density_std
        
        rounds_mean = sum(all_rounds) / len(all_rounds)
        rounds_std = (sum((x - rounds_mean) ** 2 for x in all_rounds) / len(all_rounds)) ** 0.5
        rounds_threshold = rounds_mean + 2 * rounds_std
        
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
