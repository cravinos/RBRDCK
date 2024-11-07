from typing import Dict, List
from agents.base_review_agent import BaseReviewAgent
from github.PullRequest import PullRequest
from agents.scanners.vulnerability_scanner import VulnerabilityScanner
from utils.diff_parser import FileDiff
import logging
import re

logger = logging.getLogger(__name__)

class SecurityAgent(BaseReviewAgent):
    def __init__(self):
        super().__init__()
        self.security_patterns = self._load_security_patterns()
        self.vulnerability_scanner = VulnerabilityScanner()
        
    async def review_security(self, pr: PullRequest, diff: str, previous_comments: str) -> Dict:
        """Reviews code for security vulnerabilities and best practices."""
        try:
            # Get relevant files for security review
            relevant_diffs = await self.get_relevant_files(diff, [
                '*.*'  # Check all files for security issues
            ])
            
            if not relevant_diffs:
                return {"status": "no_files", "message": "No files to review for security."}

            results = {
                "vulnerabilities": [],
                "security_smells": [],
                "recommendations": [],
                "severity_score": 0.0
            }
            
            # Scan for known vulnerabilities
            scan_results = await self.vulnerability_scanner.scan(relevant_diffs)
            results["vulnerabilities"].extend(scan_results)
            
            # Check for security patterns
            for filename, diff_content in relevant_diffs.items():
                pattern_matches = await self._check_security_patterns(filename, diff_content)
                results["security_smells"].extend(pattern_matches)
            
            # Calculate severity score
            results["severity_score"] = self._calculate_severity_score(results)
            
            # Generate recommendations
            results["recommendations"] = self._generate_security_recommendations(results)
            
            return results
            
        except Exception as e:
            logger.error(f"Error in security review: {e}", exc_info=True)
            return {"status": "error", "message": str(e)}

    def _load_security_patterns(self) -> Dict:
        """Loads security patterns and anti-patterns."""
        return {
            "hardcoded_secrets": r"(?i)(password|secret|key|token|api_key).*?['\"]([^'\"]+)['\"]",
            "sql_injection": r"(?i)(execute|raw|cursor\.execute).*?\+",
            "xss_vulnerable": r"(?i)innerHTML|document\.write\(",
            "insecure_crypto": r"(?i)(md5|sha1)\(",
            "command_injection": r"(?i)(exec|eval|system|popen)\("
        }

    async def _check_security_patterns(self, filename: str, diff_content: FileDiff) -> List[Dict]:
        """Checks for security anti-patterns in the code."""
        matches = []
        for pattern_name, pattern in self.security_patterns.items():
            for match in re.finditer(pattern, diff_content.content):
                matches.append({
                    "type": pattern_name,
                    "file": filename,
                    "line": self._get_line_number(diff_content, match.start()),
                    "snippet": match.group(0),
                    "severity": "HIGH" if pattern_name in ["hardcoded_secrets", "command_injection"] else "MEDIUM"
                })
        return matches

    def _calculate_severity_score(self, results: Dict) -> float:
        """Calculates overall security severity score."""
        severity_weights = {"HIGH": 1.0, "MEDIUM": 0.5, "LOW": 0.2}
        total_score = 0.0
        
        for vuln in results["vulnerabilities"]:
            total_score += severity_weights.get(vuln["severity"], 0.2)
        
        for smell in results["security_smells"]:
            total_score += severity_weights.get(smell["severity"], 0.2)
            
        return min(10.0, total_score)  # Cap at 10.0

    def _generate_security_recommendations(self, results: Dict) -> List[Dict]:
        """Generates security recommendations based on findings."""
        recommendations = []
        
        if results["vulnerabilities"]:
            recommendations.append({
                "priority": "HIGH",
                "title": "Fix Critical Security Vulnerabilities",
                "description": "Address the following security vulnerabilities immediately:",
                "items": [v["description"] for v in results["vulnerabilities"]]
            })
            
        if results["security_smells"]:
            recommendations.append({
                "priority": "MEDIUM",
                "title": "Address Security Code Smells",
                "description": "Improve code security by addressing these issues:",
                "items": [f"Replace {s['type']} in {s['file']}" for s in results["security_smells"]]
            })
            
        return recommendations

    def _get_line_number(self, diff_content: FileDiff, match_position: int) -> int:
        """Calculate the actual line number in the file from a position in the diff."""
        try:
            # Split content up to the match position
            content_before = diff_content.content[:match_position]
            # Count the number of newlines
            line_count = content_before.count('\n') + 1
            
            # Parse the @@ headers to get the starting line number
            hunk_headers = re.finditer(r'@@ -\d+,\d+ \+(\d+),\d+ @@', diff_content.content)
            start_line = 1
            
            for header in hunk_headers:
                header_pos = header.start()
                if header_pos > match_position:
                    break
                start_line = int(header.group(1))
            
            return start_line + line_count - 1
        except Exception as e:
            logger.error(f"Error calculating line number: {e}")
            return 0