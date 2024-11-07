# agents/test_coverage_agent.py
from typing import Dict, List
from agents.base_review_agent import BaseReviewAgent
from github.PullRequest import PullRequest
from utils.github_helper import get_test_coverage
import logging

logger = logging.getLogger(__name__)

class TestCoverageAgent(BaseReviewAgent):
    """Agent for reviewing test coverage and suggesting test improvements."""

    def __init__(self):
        super().__init__()

    async def review_test_coverage(self, pr: PullRequest, diff: str, previous_comments: str) -> str:
        """
        Reviews test coverage in the pull request.
        
        Args:
            pr: The pull request object
            diff: The pull request diff
            previous_comments: Previous review comments
            
        Returns:
            str: The test coverage review
        """
        try:
            # Get relevant files for test coverage review
            relevant_diffs = await self.get_relevant_files(diff, [
                '*.py', '*.js', '*.ts', '*.java',  # Source files
                '*test*.py', '*_test.js', '*.test.ts', '*Test.java',  # Test files
                'tests/*', '__tests__/*', 'test/*'  # Test directories
            ])
            
            if not relevant_diffs:
                return "No testable files found to review."

            formatted_diff = await self.format_diff_for_review(relevant_diffs)
            
            # Get test coverage analysis
            coverage_analysis = get_test_coverage(pr)
            prompt = self.create_test_coverage_prompt(formatted_diff, previous_comments, coverage_analysis)
            
            response = await self.llm.call(prompt)
            if not response or not response.strip():
                logger.error("Empty test coverage review generated.")
                return "Error: Test coverage review returned an empty response."
            return response
        except Exception as e:
            logger.error(f"Error generating test coverage review: {e}")
            return f"Error generating test coverage review: {str(e)}"

    def create_test_coverage_prompt(self, diff: str, previous_comments: str, analysis: Dict) -> str:
        """Creates a prompt for test coverage review."""
        prompt = f"""
        You are an expert test coverage reviewer. Your task is to ensure adequate test coverage for code changes.

        **Coverage Analysis:**
        {self._format_coverage_summary(analysis.get('summary', {}))}

        **Files Changed:**
        {diff}

        **Context:**
        Previous comments on this pull request:
        {previous_comments}

        **Instructions:**
        1. Review the test coverage analysis and changed files
        2. Identify areas requiring additional tests:
           - New functionality without tests
           - Modified code without corresponding test updates
           - Edge cases that should be tested
        3. Provide specific test suggestions using code blocks
        4. Include example test cases where helpful

        Please provide your review below:
        """
        return prompt

    def _format_coverage_summary(self, summary: Dict) -> str:
        """Formats the coverage summary for the prompt."""
        return f"""
        - Total Source Files: {summary.get('total_source_files', 0)}
        - Total Test Files: {summary.get('total_test_files', 0)}
        - Test Coverage Ratio: {summary.get('test_coverage_ratio', 0):.2f}
        - Untested Files: {summary.get('untested_files_count', 0)}
        - New Tests Added: {'Yes' if summary.get('has_new_tests', False) else 'No'}
        - Coverage Gaps: {summary.get('coverage_gaps_count', 0)}
        """