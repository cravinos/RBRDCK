# agents/dependency_review_agent.py
from typing import Dict, List
from agents.base_review_agent import BaseReviewAgent
from github.PullRequest import PullRequest
from utils.github_helper import analyze_dependencies
import logging

logger = logging.getLogger(__name__)

class DependencyReviewAgent(BaseReviewAgent):
    """Agent for reviewing dependency changes and security implications."""

    def __init__(self):
        super().__init__()

    def review_dependencies(self, pr: PullRequest, diff: str, previous_comments: str) -> str:
        """
        Reviews dependency changes in the pull request.
        
        Args:
            pr: The pull request object
            diff: The pull request diff
            previous_comments: Previous review comments
            
        Returns:
            str: The dependency review
        """
        try:
            # Get relevant files for dependency review
            relevant_diffs = self.get_relevant_files(diff, [
                'requirements.txt', 'setup.py', 'Pipfile', 'pyproject.toml',  # Python
                'package.json', 'package-lock.json', 'yarn.lock',  # Node.js
                'pom.xml', 'build.gradle', '*.csproj',  # Java/C#
                'Gemfile', 'Gemfile.lock',  # Ruby
                'go.mod', 'go.sum'  # Go
            ])
            
            if not relevant_diffs:
                return "No dependency files found to review."

            formatted_diff = self.format_diff_for_review(relevant_diffs)
            
            # Get dependency analysis
            dependency_analysis = analyze_dependencies(pr)
            prompt = self.create_dependency_prompt(formatted_diff, previous_comments, dependency_analysis)
            
            response = self.llm.call(prompt)
            if not response.strip():
                logger.error("Empty dependency review generated.")
                return "Error: Dependency review returned an empty response."
            return response
        except Exception as e:
            logger.error(f"Error generating dependency review: {e}", exc_info=True)
            return f"Error generating dependency review: {str(e)}"

    def create_dependency_prompt(self, diff: str, previous_comments: str, analysis: Dict) -> str:
        """Creates a prompt for dependency review."""
        prompt = f"""
        You are an expert dependency reviewer. Your task is to analyze dependency changes for security and compatibility issues.

        **Dependency Analysis:**
        {self._format_dependency_analysis(analysis)}

        **Files Changed:**
        {diff}

        **Context:**
        Previous comments on this pull request:
        {previous_comments}

        **Instructions:**
        1. Review the dependency changes and analysis results
        2. Evaluate:
           - Security implications of dependency changes
           - Version compatibility issues
           - Breaking changes in major updates
           - Best practices for dependency management
        3. Provide specific recommendations
        4. Suggest alternative dependencies if relevant

        Please provide your review below:
        """
        return prompt

    def _format_dependency_analysis(self, analysis: Dict) -> str:
        """Formats the dependency analysis for the prompt."""
        summary = analysis.get('summary', {})
        formatted = []
        
        formatted.append("Changes Summary:")
        formatted.append(f"- Files Changed: {summary.get('total_files_changed', 0)}")
        formatted.append(f"- Dependencies Added: {summary.get('total_dependencies_added', 0)}")
        formatted.append(f"- Dependencies Removed: {summary.get('total_dependencies_removed', 0)}")
        formatted.append(f"- Dependencies Updated: {summary.get('total_dependencies_updated', 0)}")
        formatted.append(f"- Security Alerts: {summary.get('security_alerts_count', 0)}")
        formatted.append(f"- Major Updates: {summary.get('major_updates_count', 0)}")
        
        # Add security alerts if any
        security_alerts = analysis.get('security_alerts', [])
        if security_alerts:
            formatted.append("\nSecurity Alerts:")
            for alert in security_alerts:
                formatted.append(f"- {alert['alert']} in {alert['file']}")
        
        # Add major version updates if any
        major_updates = [u for u in analysis.get('updated_dependencies', []) 
                        if u.get('change_type') == 'major']
        if major_updates:
            formatted.append("\nMajor Version Updates:")
            for update in major_updates:
                formatted.append(
                    f"- {update['name']}: {update['old_version']} → {update['new_version']}"
                )
        
        return "\n".join(formatted)