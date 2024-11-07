# agents/code_quality_agent.py
from typing import Dict, List
from agents.base_review_agent import BaseReviewAgent
from github.PullRequest import PullRequest
from utils.github_helper import analyze_code_quality
from prompts.prompt_templates import create_code_quality_prompt
import logging

logger = logging.getLogger(__name__)

class CodeQualityAgent(BaseReviewAgent):
    """Agent for reviewing code quality and suggesting improvements."""
    
    def __init__(self):
        super().__init__()
        
    async def review_code_quality(self, pr: PullRequest, diff: str, previous_comments: str) -> str:
        """Reviews code quality in the pull request."""
        try:
            # Get relevant files for code quality review
            relevant_diffs = await self.get_relevant_files(diff, [
                '*.py', '*.js', '*.ts', '*.java', '*.cpp', '*.cs', '*.go', '*.rb'
            ])
            
            if not relevant_diffs:
                return "No code files found to review."
                
            formatted_diff = await self.format_diff_for_review(relevant_diffs)
            
            # Get code quality analysis
            quality_analysis = analyze_code_quality(pr)
            prompt = create_code_quality_prompt(formatted_diff, previous_comments, quality_analysis)
            
            return await self.llm.call(prompt)
        except Exception as e:
            logger.error(f"Error generating code quality review: {e}")
            return f"Error generating code quality review: {str(e)}"