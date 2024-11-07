from typing import Dict
from .hub import BaseIntegration
import logging
from github import Github
from github.PullRequest import PullRequest

logger = logging.getLogger(__name__)

class GitHubIntegration(BaseIntegration):
    def __init__(self, token: str = None):
        self.token = token
        self.client = Github(token) if token else None
        
    def setup_webhook(self, config: Dict) -> Dict:
        """Setup GitHub webhook for repository."""
        try:
            repo = self.client.get_repo(f"{config['owner']}/{config['repo']}")
            webhook = repo.create_hook(
                name="web",
                config={
                    "url": config["webhook_url"],
                    "content_type": "json",
                    "secret": config.get("webhook_secret"),
                },
                events=["pull_request", "pull_request_review"],
                active=True
            )
            return {
                "id": webhook.id,
                "url": webhook.config["url"],
                "events": webhook.events
            }
        except Exception as e:
            logger.error(f"Error setting up GitHub webhook: {e}")
            raise
            
    def handle_webhook(self, payload: Dict) -> Dict:
        """Handle GitHub webhook event."""
        try:
            event_type = payload.get("action")
            pr_data = payload.get("pull_request", {})
            
            return {
                "event": event_type,
                "pr_number": pr_data.get("number"),
                "title": pr_data.get("title"),
                "author": pr_data.get("user", {}).get("login"),
                "status": pr_data.get("state")
            }
        except Exception as e:
            logger.error(f"Error handling GitHub webhook: {e}")
            raise
            
    def send_notification(self, message: str, context: Dict) -> bool:
        """Send notification as GitHub comment."""
        try:
            if not context.get("pr_number"):
                raise ValueError("PR number required for GitHub notification")
                
            repo = self.client.get_repo(context["repo"])
            pr = repo.get_pull(context["pr_number"])
            pr.create_issue_comment(message)
            return True
            
        except Exception as e:
            logger.error(f"Error sending GitHub notification: {e}")
            return False