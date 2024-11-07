from typing import Dict, List
from datetime import datetime, timedelta
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class Insight:
    title: str
    description: str
    severity: str
    metrics: List[Dict]
    recommendations: List[str]

class InsightsGenerator:
    def __init__(self):
        self.threshold_configs = self._load_threshold_configs()
        
    def _load_threshold_configs(self) -> Dict:
        """Load threshold configurations for insights."""
        return {
            "high_review_time": 3600,  # 1 hour
            "low_comment_ratio": 0.5,
            "high_issue_rate": 0.8
        }
        
    def create_report(self, metrics: List[Dict]) -> Dict:
        """Generate insights report from metrics."""
        try:
            insights = []
            
            # Generate various insights
            insights.extend(self._analyze_review_times(metrics))
            insights.extend(self._analyze_issue_patterns(metrics))
            insights.extend(self._analyze_review_effectiveness(metrics))
            
            return {
                "timestamp": datetime.utcnow().isoformat(),
                "summary": self._generate_summary(insights),
                "insights": [
                    {
                        "title": i.title,
                        "description": i.description,
                        "severity": i.severity,
                        "metrics": i.metrics,
                        "recommendations": i.recommendations
                    }
                    for i in insights
                ]
            }
            
        except Exception as e:
            logger.error(f"Error generating insights report: {e}")
            raise
            
    def _analyze_review_times(self, metrics: List[Dict]) -> List[Insight]:
        """Analyze review time patterns."""
        insights = []
        review_times = [m for m in metrics if m["name"] == "review_time"]
        
        if review_times:
            avg_review_time = sum(m["value"] for m in review_times) / len(review_times)
            if avg_review_time > self.threshold_configs["high_review_time"]:
                insights.append(Insight(
                    title="High Average Review Time",
                    description=f"Average review time of {avg_review_time:.2f} seconds exceeds threshold",
                    severity="medium",
                    metrics=[{"avg_review_time": avg_review_time}],
                    recommendations=[
                        "Consider breaking down larger PRs into smaller ones",
                        "Review complexity thresholds for automated reviews"
                    ]
                ))
                
        return insights
        
    def _analyze_issue_patterns(self, metrics: List[Dict]) -> List[Insight]:
        """Analyze patterns in issues found."""
        insights = []
        issue_metrics = [m for m in metrics if m["name"] == "issues_found"]
        
        if issue_metrics:
            issue_rate = sum(1 for m in issue_metrics if m["value"] > 0) / len(issue_metrics)
            if issue_rate > self.threshold_configs["high_issue_rate"]:
                insights.append(Insight(
                    title="High Issue Detection Rate",
                    description=f"Issues found in {issue_rate:.1%} of reviews",
                    severity="high",
                    metrics=[{"issue_rate": issue_rate}],
                    recommendations=[
                        "Review and update code quality guidelines",
                        "Consider implementing pre-commit hooks",
                        "Provide team training on common issues"
                    ]
                ))
                
        return insights
        
    def _analyze_review_effectiveness(self, metrics: List[Dict]) -> List[Insight]:
        """Analyze review effectiveness."""
        insights = []
        comment_metrics = [m for m in metrics if m["name"] == "comment_count"]
        
        if comment_metrics:
            avg_comments = sum(m["value"] for m in comment_metrics) / len(comment_metrics)
            if avg_comments < self.threshold_configs["low_comment_ratio"]:
                insights.append(Insight(
                    title="Low Review Interaction",
                    description=f"Average of {avg_comments:.1f} comments per review",
                    severity="low",
                    metrics=[{"avg_comments": avg_comments}],
                    recommendations=[
                        "Review comment threshold settings",
                        "Ensure review criteria are clear",
                        "Consider adding more specific review categories"
                    ]
                ))
                
        return insights
        
    def _generate_summary(self, insights: List[Insight]) -> str:
        """Generate a summary of insights."""
        if not insights:
            return "No significant insights found in the current time period."
            
        severity_counts = {
            "high": len([i for i in insights if i.severity == "high"]),
            "medium": len([i for i in insights if i.severity == "medium"]),
            "low": len([i for i in insights if i.severity == "low"])
        }
        
        summary_parts = [
            f"Found {len(insights)} insights:",
            *[f"- {severity}: {count} insight(s)"
              for severity, count in severity_counts.items() if count > 0]
        ]
        
        return "\n".join(summary_parts)