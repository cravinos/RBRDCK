# main.py

from typing import Dict, List, Union
from github import Github
from github.PullRequest import PullRequest
import logging
import json
from agents.review_orchestrator import ReviewOrchestrator, ReviewContext
from agents.documentation_review_agent import DocumentationReviewAgent
from agents.code_quality_agent import CodeQualityAgent
from agents.test_coverage_agent import TestCoverageAgent
from agents.dependency_review_agent import DependencyReviewAgent
from agents.security_agent import SecurityAgent
from llm.ollama_llm import OllamaLLM
from utils.github_helper import parse_review_comments
from config import GITHUB_TOKEN

logger = logging.getLogger(__name__)

class ReviewManager:
    def __init__(self):
        if not GITHUB_TOKEN:
            raise ValueError("GitHub token not found. Please set GITHUB_TOKEN in .env file")
            
        self.github = Github(GITHUB_TOKEN)
        self.orchestrator = ReviewOrchestrator()
        self.llm = OllamaLLM()
        
        # Initialize and register agents with orchestrator
        self.orchestrator.register_agent('documentation', DocumentationReviewAgent())
        self.orchestrator.register_agent('code_quality', CodeQualityAgent())
        self.orchestrator.register_agent('test_coverage', TestCoverageAgent())
        self.orchestrator.register_agent('dependencies', DependencyReviewAgent())
        self.orchestrator.register_agent('security', SecurityAgent())
        logger.info("ReviewManager initialized successfully")

    @classmethod
    async def create(cls):
        """Factory method to create and initialize ReviewManager with async operations"""
        manager = cls()
        if not await manager.llm.check_connection():
            raise RuntimeError("Ollama service is not running. Please start Ollama first.")
        return manager

    async def review_pr(self, repo_name: str, pr_number: int, options: Dict = None):
        """Review a pull request with all available agents"""
        try:
            # Get PR details
            repo = self.github.get_repo(repo_name)
            pr = repo.get_pull(pr_number)
            
            # Get PR diff as text
            files = pr.get_files()
            if not files:
                raise ValueError("No files found in pull request")
                
            # Get patches from all files
            diff_text = ""
            for file in files:
                if hasattr(file, 'patch') and file.patch:
                    diff_text += f"diff --git a/{file.filename} b/{file.filename}\n"
                    diff_text += file.patch + "\n"
            
            if not diff_text:
                raise ValueError("No diff content found in pull request")
                
            previous_comments = [comment.body for comment in pr.get_comments()]
            
            # Create review context
            context = ReviewContext(pr, diff_text, "\n".join(previous_comments))
            
            # Conduct review through orchestrator
            review_results = await self.orchestrator.conduct_review(context)
            
            # Post results to GitHub
            await self._post_review_to_github(pr, review_results)
            
            return review_results
            
        except Exception as e:
            logger.error(f"Error reviewing PR #{pr_number}: {e}")
            raise
            
    async def _post_review_to_github(self, pr: PullRequest, review_results: Dict):
        """Posts review results as comments on GitHub PR."""
        try:
            # First, post a general review comment
            review_body = "# AI Code Review Results\n\n"
            
            for agent_type, review in review_results['reviews'].items():
                if isinstance(review, dict) and review.get('status') == 'error':
                    continue
                    
                if isinstance(review, dict) and agent_type == 'security':
                    # Add security findings to the main review
                    review_body += f"\n## 🔒 Security Review\n\n"
                    for vuln in review.get('vulnerabilities', []):
                        review_body += f"- **{vuln['severity']} Severity Issue** in `{vuln['file']}` line {vuln['line']}\n"
                        review_body += f"  - {vuln['description']}\n"
                    
                    if review.get('recommendations'):
                        review_body += "\n### Recommendations:\n"
                        for rec in review['recommendations']:
                            review_body += f"\n#### {rec['title']} (Priority: {rec['priority']})\n"
                            review_body += f"{rec['description']}\n"
                            for item in rec['items']:
                                review_body += f"- {item}\n"
                else:
                    # Add other reviews
                    review_body += f"\n## {agent_type.replace('_', ' ').title()} Review\n\n"
                    review_body += str(review) + "\n"
            
            # Create the review without inline comments
            pr.create_review(
                body=review_body,
                event='COMMENT'
            )
            
            # Post security issues as separate comments
            if isinstance(review_results['reviews'].get('security'), dict):
                security_review = review_results['reviews']['security']
                for vuln in security_review.get('vulnerabilities', []):
                    try:
                        pr.create_issue_comment(
                            f"🔒 **Security Issue Detected**\n\n"
                            f"**Severity:** {vuln['severity']}\n"
                            f"**File:** `{vuln['file']}`\n"
                            f"**Line:** {vuln['line']}\n\n"
                            f"**Description:** {vuln['description']}"
                        )
                    except Exception as e:
                        logger.warning(f"Failed to create security comment: {e}")
        
        except Exception as e:
            logger.error(f"Error posting review to GitHub: {e}")
            raise

async def main():
    try:
        review_manager = await ReviewManager.create()
        results = await review_manager.review_pr("owner/repo", 123)
        print(json.dumps(results, indent=2))
    except Exception as e:
        logger.error(f"Error in main: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())
