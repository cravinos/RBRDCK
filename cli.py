# cli.py
from typing import Dict, List, Optional
import argparse
import logging
from github import Github
from config import GITHUB_TOKEN, REPO_NAME, LOG_FORMAT, LOG_LEVEL
from utils.github_helper import (
    get_open_pull_requests,
    get_pull_request_diff,
    post_review_comment,
    get_previous_comments
)
from agents.documentation_review_agent import DocumentationReviewAgent
from agents.code_quality_agent import CodeQualityAgent
from agents.test_coverage_agent import TestCoverageAgent
from agents.dependency_review_agent import DependencyReviewAgent

def setup_logging():
    """Configures logging for the application."""
    logging.basicConfig(level=LOG_LEVEL, format=LOG_FORMAT)
    return logging.getLogger(__name__)

logger = setup_logging()

class ReviewManager:
    """Manages the review process across different review agents."""
    
    def __init__(self):
        self.github_client = Github(GITHUB_TOKEN)
        self.repo = self.github_client.get_repo(REPO_NAME)
        self.agents = {
            'documentation': DocumentationReviewAgent(),
            'code_quality': CodeQualityAgent(),
            'test_coverage': TestCoverageAgent(),
            'dependencies': DependencyReviewAgent()
        }

    def review_pr(self, pr_number: Optional[int] = None, review_types: Optional[List[str]] = None):
        """
        Reviews pull requests using specified review types.
        
        Args:
            pr_number: Optional PR number to review
            review_types: List of review types to perform ('all' or specific types)
        """
        # Get pull requests to review
        if pr_number:
            pull_requests = [self.repo.get_pull(pr_number)]
        else:
            pull_requests = get_open_pull_requests(self.repo)

        # Determine which review types to run
        available_review_types = list(self.agents.keys())
        if not review_types or 'all' in review_types:
            review_types = available_review_types
        else:
            review_types = [rt for rt in review_types if rt in available_review_types]

        for pr in pull_requests:
            try:
                logger.info(f"Reviewing PR #{pr.number}: {pr.title}")
                
                # Get PR context
                diff = get_pull_request_diff(pr)
                if not diff:
                    logger.warning(f"No diff found for PR #{pr.number}")
                    continue

                previous_comments = get_previous_comments(pr)

                # Run each selected review type
                for review_type in review_types:
                    try:
                        self._perform_review(pr, diff, previous_comments, review_type)
                    except Exception as e:
                        logger.error(
                            f"Error performing {review_type} review for PR #{pr.number}: {e}", 
                            exc_info=True
                        )

            except Exception as e:
                logger.error(f"Error processing PR #{pr.number}: {e}", exc_info=True)

    def _perform_review(self, pr, diff: str, previous_comments: str, review_type: str):
        """
        Performs a specific type of review on a pull request.
        
        Args:
            pr: Pull request object
            diff: The pull request diff
            previous_comments: Previous review comments
            review_type: Type of review to perform
        """
        logger.info(f"Performing {review_type} review for PR #{pr.number}")
        
        agent = self.agents[review_type]
        review = None

        if review_type == 'documentation':
            review = agent.review_documentation(diff, previous_comments)
        elif review_type == 'code_quality':
            review = agent.review_code_quality(pr, diff, previous_comments)
        elif review_type == 'test_coverage':
            review = agent.review_test_coverage(pr, diff, previous_comments)
        elif review_type == 'dependencies':
            review = agent.review_dependencies(pr, diff, previous_comments)

        if review and review.strip():
            # Format the review with a header indicating the review type
            formatted_review = f"""
## {review_type.replace('_', ' ').title()} Review

{review}
"""
            post_review_comment(pr, formatted_review)
            logger.info(f"{review_type} review posted for PR #{pr.number}")
        else:
            logger.warning(f"Empty {review_type} review generated for PR #{pr.number}")

def main():
    parser = argparse.ArgumentParser(description="AI-powered Pull Request Reviewer")
    parser.add_argument(
        "--pr", 
        type=int, 
        help="PR number to review. If not provided, all open PRs will be reviewed."
    )
    parser.add_argument(
        "--review-types",
        nargs="+",
        choices=['all', 'documentation', 'code_quality', 'test_coverage', 'dependencies'],
        default=['all'],
        help="Types of reviews to perform. Use 'all' for all review types."
    )
    parser.add_argument(
        "--parallel",
        action="store_true",
        help="Run reviews in parallel (not implemented yet)"
    )
    args = parser.parse_args()

    manager = ReviewManager()
    manager.review_pr(args.pr, args.review_types)

if __name__ == "__main__":
    main()