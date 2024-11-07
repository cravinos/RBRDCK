# agents/documentation_review_agent.py
from typing import Dict, List
from agents.base_review_agent import BaseReviewAgent
from prompts.prompt_templates import create_documentation_review_prompt
import logging

logger = logging.getLogger(__name__)

class DocumentationReviewAgent(BaseReviewAgent):
    """Agent for reviewing documentation changes and standards."""
    
    def __init__(self):
        super().__init__()
        
    async def review_documentation(self, diff: str, previous_comments: str) -> str:
        """
        Reviews documentation changes in the pull request.
        
        Args:
            diff: The pull request diff
            previous_comments: Previous review comments
            
        Returns:
            str: The documentation review
        """
        # Get relevant files for documentation review
        relevant_diffs = await self.get_relevant_files(diff, [
            '*.py', '*.js', '*.java',  # Source files
            '*.md', '*.rst', '*.txt',  # Documentation files
            'README*', 'CONTRIBUTING*', 'CHANGELOG*'  # Project docs
        ])
        
        if not relevant_diffs:
            return "No documentation-related changes found to review."
            
        formatted_diff = await self.format_diff_for_review(relevant_diffs)
        prompt = create_documentation_review_prompt(formatted_diff, previous_comments)
        
        return await self.llm_call(prompt)