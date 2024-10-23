# agents/code_quality_agent.py
# agents/test_coverage_agent.py

from llm.ollama_llm import OllamaLLM
from github.PullRequest import PullRequest
from utils.github_helper import get_test_coverage  # Add this import
import logging
from typing import Dict

logger = logging.getLogger(__name__)

class TestCoverageAgent:
    def __init__(self):
        self.llm = OllamaLLM()

    def review_test_coverage(self, pr: PullRequest, diff: str, previous_comments: str) -> str:
        try:
            coverage_analysis = get_test_coverage(pr)
            prompt = self.create_test_coverage_prompt(diff, previous_comments, coverage_analysis)
            
            response = self.llm.call(prompt)
            if not response.strip():
                logger.error("Empty test coverage review generated.")
                return "Error: Test coverage review returned an empty response."
            return response
        except Exception as e:
            logger.error(f"Error generating test coverage review: {e}", exc_info=True)
            return f"Error generating test coverage review: {str(e)}"

    def create_test_coverage_prompt(self, diff: str, previous_comments: str, analysis: Dict) -> str:
        prompt = f"""
        You are an expert test coverage reviewer. Your task is to ensure adequate test coverage for code changes.

        **Coverage Analysis:**
        {self._format_coverage_summary(analysis.get('summary', {}))}

        Untested Files:
        {self._format_untested_files(analysis.get('untested_files', []))}

        Coverage Gaps:
        {self._format_coverage_gaps(analysis.get('coverage_gaps', []))}

        **Context:**
        Previous comments on this pull request:
        {previous_comments}

        **Code Diff for Review:**
        {diff}

        **Instructions:**
        1. Review the test coverage analysis
        2. Identify areas requiring additional tests:
           - New functionality without tests
           - Modified code without corresponding test updates
           - Edge cases that should be tested
        3. Provide specific test suggestions using code blocks
        4. Include example test cases where helpful
        5. Suggest test structure improvements

        Format your review with specific suggestions for new tests or test improvements.
        For each suggestion:
        - **Issue Description**

        ```suggestion
        Your suggested test code
        ```

        **File:** `file_path`

        **Line:** line_number

        Please provide your review below:
        """
        return prompt

    def _format_coverage_summary(self, summary: Dict) -> str:
        return f"""
        - Total Source Files: {summary.get('total_source_files', 0)}
        - Total Test Files: {summary.get('total_test_files', 0)}
        - Test Coverage Ratio: {summary.get('test_coverage_ratio', 0):.2f}
        - Untested Files: {summary.get('untested_files_count', 0)}
        - New Tests Added: {'Yes' if summary.get('has_new_tests', False) else 'No'}
        """

    def _format_untested_files(self, untested_files: list) -> str:
        return "\n".join([f"- {file}" for file in untested_files]) if untested_files else "No untested files detected."

    def _format_coverage_gaps(self, gaps: list) -> str:
        return "\n".join([f"- {gap['file']}: {gap['suggestion']}" for gap in gaps]) if gaps else "No specific coverage gaps det"