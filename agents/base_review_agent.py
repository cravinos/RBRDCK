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