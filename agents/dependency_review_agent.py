# agents/dependency_review_agent.py

# agents/dependency_review_agent.py

from llm.ollama_llm import OllamaLLM
from github.PullRequest import PullRequest
from utils.github_helper import analyze_dependencies  # Add this import
import logging
from typing import Dict

logger = logging.getLogger(__name__)

class DependencyReviewAgent:
    def __init__(self):
        self.llm = OllamaLLM()

    def review_dependencies(self, pr: PullRequest, diff: str, previous_comments: str) -> str:
        try:
            dependency_analysis = analyze_dependencies(pr)
            prompt = self.create_dependency_prompt(diff, previous_comments, dependency_analysis)
            
            response = self.llm.call(prompt)
            if not response.strip():
                logger.error("Empty dependency review generated.")
                return "Error: Dependency review returned an empty response."
            return response
        except Exception as e:
            logger.error(f"Error generating dependency review: {e}", exc_info=True)
            return f"Error generating dependency review: {str(e)}"

    def create_dependency_prompt(self, diff: str, previous_comments: str, analysis: Dict) -> str:
        prompt = f"""
        You are an expert dependency reviewer. Your task is to analyze dependency changes for security and compatibility issues.

        **Dependency Analysis:**
        {self._format_dependency_summary(analysis.get('summary', {}))}

        Security Alerts:
        {self._format_security_alerts(analysis.get('security_alerts', []))}

        Major Updates:
        {self._format_major_updates(analysis.get('updated_dependencies', []))}

        **Context:**
        Previous comments on this pull request:
        {previous_comments}

        **Dependency Changes:**
        {diff}

        **Instructions:**
        1. Review the dependency analysis results
        2. Evaluate:
           - Security implications of dependency changes
           - Version compatibility issues
           - Breaking changes in major updates
           - Best practices for dependency management
        3. Provide specific recommendations
        4. Suggest alternative dependencies if relevant
        5. Include upgrade/migration guidance for major changes

        Format your review with specific suggestions and concerns.
        For each issue:
        - **Issue Description**

        ```suggestion
        Your suggested dependency change
        ```

        **File:** `file_path`

        **Line:** line_number

        Please provide your review below:
        """
        return prompt

    def _format_dependency_summary(self, summary: Dict) -> str:
        return f"""
        - Files Changed: {summary.get('total_files_changed', 0)}
        - Dependencies Added: {summary.get('total_dependencies_added', 0)}
        - Dependencies Removed: {summary.get('total_dependencies_removed', 0)}
        - Dependencies Updated: {summary.get('total_dependencies_updated', 0)}
        - Security Alerts: {summary.get('security_alerts_count', 0)}
        - Major Updates: {summary.get('major_updates_count', 0)}
        """

    def _format_security_alerts(self, alerts: list) -> str:
        return "\n".join([f"- {alert['alert']} in {alert['file']}" for alert in alerts]) if alerts else "No security alerts detected."

    def _format_major_updates(self, updates: list) -> str:
        major_updates = [u for u in updates if u.get('change_type') == 'major']
        if not major_updates:
            return "No major version updates detected."
        return "\n".join([
            f"- {update['name']}: {update['old_version']} → {update['new_version']}"
            for update in major_updates
        ])