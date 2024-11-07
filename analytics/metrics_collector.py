from typing import Dict, List, Optional
from datetime import datetime
import logging
from dataclasses import dataclass
import json

logger = logging.getLogger(__name__)

@dataclass
class Metric:
    timestamp: datetime
    name: str
    value: float
    labels: Dict[str, str]

class MetricsCollector:
    def __init__(self, storage_path: str = "metrics"):
        self.storage_path = storage_path
        self._ensure_storage_path()
        
    def _ensure_storage_path(self):
        """Ensure metrics storage path exists."""
        import os
        os.makedirs(self.storage_path, exist_ok=True)
        
    def add_metrics(self, metrics: List[Metric]):
        """Add multiple metrics."""
        try:
            timestamp = datetime.utcnow()
            filename = f"{timestamp.strftime('%Y%m%d')}_metrics.json"
            filepath = f"{self.storage_path}/{filename}"
            
            metrics_data = [
                {
                    "timestamp": m.timestamp.isoformat(),
                    "name": m.name,
                    "value": m.value,
                    "labels": m.labels
                }
                for m in metrics
            ]
            
            with open(filepath, "a") as f:
                for metric in metrics_data:
                    f.write(json.dumps(metric) + "\n")
                    
        except Exception as e:
            logger.error(f"Error adding metrics: {e}")
            
    def get_metrics(self,
                    start_date: Optional[datetime] = None,
                    end_date: Optional[datetime] = None,
                    metric_name: Optional[str] = None) -> List[Metric]:
        """Retrieve metrics with optional filters."""
        metrics = []
        try:
            import glob
            import os
            
            # Determine which metric files to read based on date range
            if start_date:
                start_day = start_date.strftime('%Y%m%d')
            else:
                start_day = "00000000"
                
            if end_date:
                end_day = end_date.strftime('%Y%m%d')
            else:
                end_day = "99999999"
                
            metric_files = glob.glob(f"{self.storage_path}/*_metrics.json")
            
            for metric_file in metric_files:
                day = os.path.basename(metric_file)[:8]
                if start_day <= day <= end_day:
                    with open(metric_file, "r") as f:
                        for line in f:
                            try:
                                metric_data = json.loads(line)
                                if self._matches_filters(metric_data, metric_name):
                                    metrics.append(Metric(
                                        timestamp=datetime.fromisoformat(metric_data["timestamp"]),
                                        name=metric_data["name"],
                                        value=metric_data["value"],
                                        labels=metric_data["labels"]
                                    ))
                            except json.JSONDecodeError:
                                logger.error(f"Invalid JSON in metric file: {metric_file}")
                                
            return sorted(metrics, key=lambda x: x.timestamp)
            
        except Exception as e:
            logger.error(f"Error retrieving metrics: {e}")
            return []
            
    def _matches_filters(self,
                        metric_data: Dict,
                        metric_name: Optional[str]) -> bool:
        """Check if metric matches the specified filters."""
        if metric_name and metric_data.get("name") != metric_name:
            return False
        return True