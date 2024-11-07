from typing import Dict, Optional
import logging
from datetime import datetime
import json

logger = logging.getLogger(__name__)

class AuditLogger:
    def __init__(self, storage_path: str = "audit_logs"):
        self.storage_path = storage_path
        self._ensure_storage_path()
        
    def _ensure_storage_path(self):
        """Ensure audit log storage path exists."""
        import os
        os.makedirs(self.storage_path, exist_ok=True)
        
    def log_compliance_check(self, pr_number: int, report: Dict):
        """Log compliance check results."""
        self._log_event(
            event_type="compliance_check",
            pr_number=pr_number,
            details=report
        )
        
    def log_review_action(self, pr_number: int, action: str, details: Dict):
        """Log review-related action."""
        self._log_event(
            event_type="review_action",
            pr_number=pr_number,
            action=action,
            details=details
        )
        
    def log_policy_violation(self, pr_number: int, policy_id: str, details: Dict):
        """Log policy violation."""
        self._log_event(
            event_type="policy_violation",
            pr_number=pr_number,
            policy_id=policy_id,
            details=details
        )
        
    def _log_event(self, event_type: str, **kwargs):
        """Log an audit event."""
        try:
            timestamp = datetime.utcnow()
            log_entry = {
                "timestamp": timestamp.isoformat(),
                "event_type": event_type,
                **kwargs
            }
            
            filename = f"{timestamp.strftime('%Y%m')}_audit.log"
            filepath = f"{self.storage_path}/{filename}"
            
            with open(filepath, "a") as f:
                f.write(json.dumps(log_entry) + "\n")
                
        except Exception as e:
            logger.error(f"Error logging audit event: {e}")
            
    def get_logs(self, 
                 start_date: Optional[datetime] = None,
                 end_date: Optional[datetime] = None,
                 event_type: Optional[str] = None,
                 pr_number: Optional[int] = None) -> List[Dict]:
        """Retrieve audit logs with optional filters."""
        logs = []
        try:
            import glob
            import os
            
            # Determine which log files to read based on date range
            if start_date:
                start_month = start_date.strftime('%Y%m')
            else:
                start_month = "000000"
                
            if end_date:
                end_month = end_date.strftime('%Y%m')
            else:
                end_month = "999999"
                
            log_files = glob.glob(f"{self.storage_path}/*_audit.log")
            
            for log_file in log_files:
                month = os.path.basename(log_file)[:6]
                if start_month <= month <= end_month:
                    with open(log_file, "r") as f:
                        for line in f:
                            try:
                                log_entry = json.loads(line)
                                if self._matches_filters(log_entry, event_type, pr_number):
                                    logs.append(log_entry)
                            except json.JSONDecodeError:
                                logger.error(f"Invalid JSON in log file: {log_file}")
                                
            return sorted(logs, key=lambda x: x["timestamp"])
            
        except Exception as e:
            logger.error(f"Error retrieving audit logs: {e}")
            return []
            
    def _matches_filters(self, 
                        log_entry: Dict,
                        event_type: Optional[str],
                        pr_number: Optional[int]) -> bool:
        """Check if log entry matches the specified filters."""
        if event_type and log_entry.get("event_type") != event_type:
            return False
        if pr_number and log_entry.get("pr_number") != pr_number:
            return False
        return True