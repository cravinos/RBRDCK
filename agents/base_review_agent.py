# agents/base_review_agent.py
from typing import Dict, List
from llm.ollama_llm import OllamaLLM
from utils.diff_parser import DiffParser, FileDiff
import logging

logger = logging.getLogger(__name__)

class BaseReviewAgent:
    """Base class for review agents with common diff handling."""
    
    def __init__(self):
        self.diff_parser = DiffParser()
        self.llm = OllamaLLM()
        
    def get_relevant_files(self, diff: str, patterns: List[str]) -> Dict[str, FileDiff]:
        """Gets relevant file changes for this agent's review."""
        return self.diff_parser.get_relevant_diff_content(diff, patterns)
        
    def format_diff_for_review(self, diffs: Dict[str, FileDiff]) -> str:
        """Formats diff content for LLM review."""
        formatted = []
        for filename, diff in diffs.items():
            formatted.append(f"File: {filename}")
            formatted.append("```")
            formatted.append(diff.content)
            formatted.append("```")
            formatted.append(f"Added lines: {diff.added_lines}")
            formatted.append(f"Removed lines: {diff.removed_lines}")
            formatted.append(f"Modified lines: {diff.modified_lines}")
            formatted.append("")
        return "\n".join(formatted)

    def _validate_response(self, response: str) -> bool:
        """Validates if the response is meaningful."""
        if not response or not response.strip():
            return False
        if response.startswith('Error:'):
            return False
        return True

    def _handle_empty_response(self, agent_type: str) -> str:
        """Handles empty or error responses."""
        return f"The {agent_type} review could not be completed. Please try again later."

    def _format_review(self, review: str, agent_type: str) -> str:
        """Formats the review response with proper headers and structure."""
        if not self._validate_response(review):
            return self._handle_empty_response(agent_type)
            
        formatted_review = f"""
## {agent_type} Review

{review}

---
_Review generated by {agent_type} using {self.llm.model}_
"""
        return formatted_review.strip()