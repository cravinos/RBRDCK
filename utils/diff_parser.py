# utils/diff_parser.py
from dataclasses import dataclass
from typing import Dict, List
import fnmatch
import logging
import re

logger = logging.getLogger(__name__)

@dataclass
class FileDiff:
    content: str
    added_lines: int
    removed_lines: int
    modified_lines: int

class DiffParser:
    """Parser for git diff output to extract meaningful file changes."""
    
    @staticmethod
    async def parse_diff(diff_text: str) -> Dict[str, FileDiff]:
        """
        Parses a git diff string into structured file changes.
        """
        try:
            if isinstance(diff_text, (list, tuple)):
                diff_text = "\n".join(str(line) for line in diff_text)
            elif not isinstance(diff_text, str):
                diff_text = str(diff_text)
                
            diffs = {}
            current_file = None
            current_content = []
            
            for line in diff_text.split('\n'):
                if line.startswith('diff --git'):
                    if current_file:
                        diffs[current_file] = FileDiff("\n".join(current_content))
                    current_file = line.split()[-1].lstrip('b/')
                    current_content = []
                current_content.append(line)
                
            if current_file:
                diffs[current_file] = FileDiff("\n".join(current_content))
                
            return diffs
        except Exception as e:
            logger.error(f"Error parsing diff content: {e}")
            return {}

    async def get_relevant_diff_content(self, diff_text: str, patterns: List[str]) -> Dict[str, FileDiff]:
        """
        Gets relevant diff content filtered by file patterns.
        
        Args:
            diff_text: Raw diff string
            file_patterns: List of file patterns to match (e.g. ['*.py', 'requirements.txt'])
            
        Returns:
            Dict of relevant file diffs
        """
        try:
            if not diff_text:
                return {}
                
            all_diffs = self._parse_diff(diff_text)
            relevant_diffs = {}
            
            for filename, diff in all_diffs.items():
                if any(fnmatch.fnmatch(filename, pattern) for pattern in patterns):
                    relevant_diffs[filename] = diff
                    
            return relevant_diffs
        except Exception as e:
            logger.error(f"Error parsing diff: {e}")
            return {}
            
    def _parse_diff(self, diff_text: str) -> Dict[str, FileDiff]:
        """Parses git diff output into structured format."""
        try:
            diffs = {}
            current_file = None
            current_content = []
            added_lines = 0
            removed_lines = 0
            modified_lines = 0
            
            for line in diff_text.split('\n'):
                if line.startswith('diff --git'):
                    if current_file:
                        # Create FileDiff for previous file
                        diffs[current_file] = FileDiff(
                            content='\n'.join(current_content),
                            added_lines=added_lines,
                            removed_lines=removed_lines,
                            modified_lines=modified_lines
                        )
                    # Reset for new file
                    current_file = line.split()[-1].lstrip('b/')
                    current_content = []
                    added_lines = 0
                    removed_lines = 0
                    modified_lines = 0
                
                current_content.append(line)
                
                # Count line changes
                if line.startswith('+') and not line.startswith('+++'):
                    added_lines += 1
                elif line.startswith('-') and not line.startswith('---'):
                    removed_lines += 1
                elif line.startswith('@@ '):
                    modified_lines += 1
            
            # Don't forget the last file
            if current_file:
                diffs[current_file] = FileDiff(
                    content='\n'.join(current_content),
                    added_lines=added_lines,
                    removed_lines=removed_lines,
                    modified_lines=modified_lines
                )
                
            return diffs
        except Exception as e:
            logger.error(f"Error parsing diff content: {e}")
            return {}
