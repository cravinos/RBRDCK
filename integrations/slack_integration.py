from typing import Dict
import logging
import requests

logger = logging.getLogger(__name__)

class SlackIntegration(BaseIntegration):
    def __init__(self, webhook_url: str = None):
        self.webhook_url = webhook_url
        
    def setup_webhook(self, config: Dict) -> Dict:
        """Store Slack webhook URL."""
        self.webhook_url = config["webhook_url"]
        return {
            "url": self.webhook_url,
            "status": "configured"
        }
        
    def handle_webhook(self, payload: Dict) -> Dict:
        """Handle Slack webhook event."""
        try:
            return {
                "event": payload.get("type"),
                "channel": payload.get("channel", {}).get("name"),
                "user": payload.get("user", {}).get("name")
            }
        except Exception as e:
            logger.error(f"Error handling Slack webhook: {e}")
            raise
            
    def send_notification(self, message: str, context: Dict) -> bool:
        """Send message to Slack channel."""
        try:
            if not self.webhook_url:
                raise ValueError("Slack webhook URL not configured")
                
            payload = {
                "text": message,
                "channel": context.get("channel"),
                "username": "RBRDCK Bot",
                "icon_emoji": ":robot_face:"
            }
            
            response = requests.post(self.webhook_url, json=payload)
            response.raise_for_status()
            return True
            
        except Exception as e:
            logger.error(f"Error sending Slack notification: {e}")
            return False