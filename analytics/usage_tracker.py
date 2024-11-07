from typing import Dict, List, Optional
from datetime import datetime, timedelta
import logging
from dataclasses import dataclass
import json

logger = logging.getLogger(__name__)

@dataclass
class UsageMetric:
    timestamp: datetime
    metric_type: str
    value: float
    context: Dict

class UsageAnalytics:
    def __init__(self):
        self.metrics_collector = MetricsCollector()
        self.insights_generator = InsightsGenerator()
        self.retention_days = 90
        
    def track_review_metrics(self, review_data: Dict):
        """Track review usage and effectiveness metrics."""
        try:
            metrics = self._extract_metrics(review_data)
            self.metrics_collector.add_metrics(metrics)
            logger.info(f"Tracked {len(metrics)} metrics for review")
            
        except Exception as e:
            logger.error(f"Error tracking review metrics: {e}")
            
    def generate_insights_report(self, timeframe: str = "7d") -> Dict:
        """Generate insights report for specified timeframe."""
        try:
            end_date = datetime.utcnow()
            start_date = self._calculate_start_date(end_date, timeframe)
            
            metrics = self.metrics_collector.get_metrics(start_date, end_date)
            return self.insights_generator.create_report(metrics)
            
        except Exception as e:
            logger.error(f"Error generating insights report: {e}")
            raise
            
    def _extract_metrics(self, review_data: Dict) -> List[UsageMetric]:
        """Extract metrics from review data."""
        metrics = []
        timestamp = datetime.utcnow()
        
        # Track review time
        metrics.append(UsageMetric(
            timestamp=timestamp,
            metric_type="review_time",
            value=review_data.get("review_time", 0),
            context={"pr_number": review_data.get("pr_number")}
        ))
        
        # Track number of comments
        metrics.append(UsageMetric(
            timestamp=timestamp,
            metric_type="comment_count",
            value=len(review_data.get("comments", [])),
            context={"pr_number": review_data.get("pr_number")}
        ))
        
        # Track issues found
        metrics.append(UsageMetric(
            timestamp=timestamp,
            metric_type="issues_found",
            value=len(review_data.get("issues", [])),
            context={"pr_number": review_data.get("pr_number")}
        ))
        
        return metrics
        
    def _calculate_start_date(self, end_date: datetime, timeframe: str) -> datetime:
        """Calculate start date based on timeframe."""
        timeframe_map = {
            "1d": timedelta(days=1),
            "7d": timedelta(days=7),
            "30d": timedelta(days=30),
            "90d": timedelta(days=90)
        }
        
        delta = timeframe_map.get(timeframe, timeframe_map["7d"])
        return end_date - delta
        
    def get_usage_statistics(self) -> Dict:
        """Get overall usage statistics."""
        try:
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=self.retention_days)
            
            metrics = self.metrics_collector.get_metrics(start_date, end_date)
            return {
                "total_reviews": len(set(m.context.get("pr_number") for m in metrics)),
                "total_comments": sum(m.value for m in metrics if m.metric_type == "comment_count"),
                "total_issues": sum(m.value for m in metrics if m.metric_type == "issues_found"),
                "avg_review_time": self._calculate_average(
                    [m.value for m in metrics if m.metric_type == "review_time"]
                )
            }
            
        except Exception as e:
            logger.error(f"Error getting usage statistics: {e}")
            raise
            
    def _calculate_average(self, values: List[float]) -> float:
        """Calculate average of values."""
        return sum(values) / len(values) if values else 0.0