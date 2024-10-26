# utils/diff_parser.py
from typing import Dict, List, NamedTuple
import re
import logging

logger = logging.getLogger(__name__)

class FileDiff(NamedTuple):
    filename: str
    content: str
    added_lines: List[int]
    removed_lines: List[int]
    modified_lines: List[int]

class DiffParser:
    """Parser for git diff output to extract meaningful file changes."""
    
    @staticmethod
    def parse_diff(diff_text: str) -> Dict[str, FileDiff]:
        """
        Parses a git diff string into structured file changes.
        """
        diffs = {}
        current_file = None
        current_content = []
        line_numbers = {'added': [], 'removed': [], 'modified': []}
        old_start = new_start = 0
        
        for line in diff_text.split('\n'):
            # New file diff starts
            if line.startswith('diff --git'):
                if current_file:
                    # Store previous file diff
                    diffs[current_file] = FileDiff(
                        filename=current_file,
                        content='\n'.join(current_content),
                        added_lines=line_numbers['added'],
                        removed_lines=line_numbers['removed'],
                        modified_lines=line_numbers['modified']
                    )
                # Reset for new file
                current_file = re.search(r'b/(.+)$', line).group(1)
                current_content = []
                line_numbers = {'added': [], 'removed': [], 'modified': []}
                
            elif line.startswith('+++') or line.startswith('---'):
                continue
                
            elif line.startswith('@@'):
                # Parse hunk header for line numbers
                match = re.match(r'@@ -(\d+),?(\d+)? \+(\d+),?(\d+)? @@', line)
                if match:
                    old_start = int(match.group(1))
                    new_start = int(match.group(3))
                    
            elif current_file:
                current_content.append(line)
                if line.startswith('+'):
                    line_numbers['added'].append(new_start)
                    new_start += 1
                elif line.startswith('-'):
                    line_numbers['removed'].append(old_start)
                    old_start += 1
                else:
                    if old_start == new_start:
                        line_numbers['modified'].append(old_start)
                    old_start += 1
                    new_start += 1
        
        # Add last file
        if current_file:
            diffs[current_file] = FileDiff(
                filename=current_file,
                content='\n'.join(current_content),
                added_lines=line_numbers['added'],
                removed_lines=line_numbers['removed'],
                modified_lines=line_numbers['modified']
            )
            
        return diffs

    def get_relevant_diff_content(self, diff_text: str, file_patterns: List[str]) -> Dict[str, FileDiff]:
        """
        Gets relevant diff content filtered by file patterns.
        
        Args:
            diff_text: Raw diff string
            file_patterns: List of file patterns to match (e.g. ['*.py', 'requirements.txt'])
            
        Returns:
            Dict of relevant file diffs
        """
        all_diffs = self.parse_diff(diff_text)
        relevant_diffs = {}
        
        for filename, file_diff in all_diffs.items():
            if any(re.match(pattern.replace('*', '.*'), filename) for pattern in file_patterns):
                relevant_diffs[filename] = file_diff
                
        return relevant_diffs
