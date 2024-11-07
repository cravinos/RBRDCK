from typing import Dict
from .hub import BaseIntegration
import logging
from jira import JIRA

logger = logging.getLogger(__name__)

class JiraIntegration(BaseIntegration):
    def __init__(self, config: Dict = None):
        self.client = None
        if config:
            self.setup_client(config)
            
    def setup_client(self, config: Dict):
        """Setup Jira client."""
        self.client = JIRA(
            server=config["server"],
            basic_auth=(config["username"], config["api_token"])
        )
        
    def setup_webhook(self, config: Dict) -> Dict:
        """Setup Jira webhook."""
        try:
            webhook = self.client.create_webhook({
                "name": "RBRDCK Integration",
                "url": config["webhook_url"],
                "events": ["jira:issue_updated", "jira:issue_created"],
                "filters": {
                    "issue-related-events-section": "true"
                }
            })
            return {
                "id": webhook["id"],
                "url": webhook["url"],
                "events": webhook["events"]
            }
        except Exception as e:
            logger.error(f"Error setting up Jira webhook: {e}")
            raise
            
    def handle_webhook(self, payload: Dict) -> Dict:
        """Handle Jira webhook event."""
        try:
            event_type = payload.get("webhookEvent")
            issue_data = payload.get("issue", {})
            
            return {
                "event": event_type,
                "issue_key": issue_data.get("key"),
                "summary": issue_data.get("fields", {}).get("summary"),
                "status": issue_data.get("fields", {}).get("status", {}).get("name")
            }
        except Exception as e:
            logger.error(f"Error handling Jira webhook: {e}")
            raise
            
    def send_notification(self, message: str, context: Dict) -> bool:
        """Add comment to Jira issue."""
        try:
            if not context.get("issue_key"):
                raise ValueError("Issue key required for Jira notification")
                
            self.client.add_comment(context["issue_key"], message)
            return True
            
        except Exception as e:
            logger.error(f"Error sending Jira notification: {e}")
            return False