# agents/code_quality_agent.py

from llm.ollama_llm import OllamaLLM
from github.PullRequest import PullRequest
from utils.github_helper import analyze_code_quality
import logging
from typing import Dict

logger = logging.getLogger(__name__)

class CodeQualityAgent:
    def __init__(self):
        self.llm = OllamaLLM()

    def review_code_quality(self, pr: PullRequest, diff: str, previous_comments: str) -> str:
        try:
            # Get code quality analysis
            quality_analysis = analyze_code_quality(pr)
            
            # Create prompt with analysis results
            prompt = self.create_code_quality_prompt(diff, previous_comments, quality_analysis)
            
            # Get LLM review
            response = self.llm.call(prompt)
            if not response.strip():
                logger.error("Empty code quality review generated.")
                return "Error: Code quality review returned an empty response."
            return response
        except Exception as e:
            logger.error(f"Error generating code quality review: {e}", exc_info=True)
            return f"Error generating code quality review: {str(e)}"

    def create_code_quality_prompt(self, diff: str, previous_comments: str, analysis: Dict) -> str:
        prompt = f"""
        You are an expert code quality reviewer. Your task is to analyze code changes and suggest improvements.

        **Analysis Results:**
        Code Complexity:
        {self._format_complexity_summary(analysis.get('summary', {}))}

        Security Concerns:
        {self._format_security_issues(analysis.get('potential_issues', []))}

        Style Issues:
        {self._format_style_issues(analysis.get('code_style', {}))}

        **Context:**
        Previous comments on this pull request:
        {previous_comments}

        **Code Diff for Review:**
        {diff}

        **Instructions:**
        1. Review the automated analysis results
        2. Identify additional code quality concerns:
           - Complex logic that needs simplification
           - Potential performance issues
           - Code duplication
           - Inconsistent naming or styling
        3. Provide specific suggestions using GitHub suggestion blocks
        4. Prioritize feedback based on severity
        5. Include explanations for why changes are recommended

        Format your review as follows:
        For each issue:
        - **Issue Description**

        ```suggestion
        Your suggested code change
        ```

        **File:** `file_path`

        **Line:** line_number

        Please provide your review below:
        """
        return prompt

    def _format_complexity_summary(self, summary: Dict) -> str:
        return f"""
        - Files Changed: {summary.get('files_changed', 0)}
        - Total Lines Changed: {summary.get('total_lines_changed', 0)}
        - Average Complexity: {summary.get('average_complexity', 0):.2f}
        - High Complexity Files: {summary.get('high_complexity_files', 0)}
        """

    def _format_security_issues(self, issues: list) -> str:
        if not issues:
            return "No security issues detected."
        return "\n".join([f"- {issue['issue']} in {issue['file']}" for issue in issues])

    def _format_style_issues(self, style_issues: Dict) -> str:
        formatted = []
        for file, issues in style_issues.items():
            for issue in issues:
                formatted.append(f"- {issue['issue']} in {file}")
        return "\n".join(formatted) if formatted else "No style issues detected."