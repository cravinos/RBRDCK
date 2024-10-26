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
from agents.review_orchestrator import ReviewOrchestrator, ReviewContext

def setup_logging():
    """Configures logging for the application."""
    logging.basicConfig(level=LOG_LEVEL, format=LOG_FORMAT)
    return logging.getLogger(__name__)

logger = setup_logging()

class ReviewManager:
    """Manages the collaborative review process for pull requests."""
    
    def __init__(self):
        self.github_client = Github(GITHUB_TOKEN)
        self.repo = self.github_client.get_repo(REPO_NAME)
        self.orchestrator = ReviewOrchestrator()

    def review_pr(self, pr_number: Optional[int] = None):
        """
        Reviews pull requests using a collaborative approach among review agents.
        
        Args:
            pr_number: Optional PR number to review. If not provided, reviews all open PRs.
        """
        # Get pull requests to review
        if pr_number:
            pull_requests = [self.repo.get_pull(pr_number)]
        else:
            pull_requests = get_open_pull_requests(self.repo)

        if not pull_requests:
            logger.info("No open pull requests found.")
            return

        for pr in pull_requests:
            try:
                logger.info(f"Reviewing PR #{pr.number}: {pr.title}")
                
                # Get PR context
                diff = get_pull_request_diff(pr)
                if not diff:
                    logger.warning(f"No diff found for PR #{pr.number}")
                    continue

                previous_comments = get_previous_comments(pr)

                # Create review context
                review_context = ReviewContext(pr, diff, previous_comments)

                # Conduct collaborative review
                try:
                    logger.info(f"Starting collaborative review for PR #{pr.number}")
                    final_review = self.orchestrator.conduct_collaborative_review(review_context)
                    
                    if final_review.strip():
                        post_review_comment(pr, final_review)
                        logger.info(f"Posted collaborative review for PR #{pr.number}")
                    else:
                        logger.warning(f"Empty review generated for PR #{pr.number}")
                        
                except Exception as e:
                    logger.error(
                        f"Error during collaborative review for PR #{pr.number}: {e}", 
                        exc_info=True
                    )

            except Exception as e:
                logger.error(f"Error processing PR #{pr.number}: {e}", exc_info=True)

    def get_review_statistics(self) -> Dict:
        """
        Gets statistics about the review process.
        
        Returns:
            Dict containing review statistics
        """
        return {
            'total_prs_reviewed': len(list(get_open_pull_requests(self.repo))),
            'agent_stats': self.orchestrator.get_agent_statistics()
        }

def main():
    parser = argparse.ArgumentParser(description="AI-powered Collaborative Pull Request Reviewer")
    parser.add_argument(
        "--pr", 
        type=int, 
        help="PR number to review. If not provided, all open PRs will be reviewed."
    )
    parser.add_argument(
        "--stats",
        action="store_true",
        help="Show review statistics"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )
    args = parser.parse_args()

    # Configure verbose logging if requested
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    manager = ReviewManager()
    
    if args.stats:
        # Display review statistics
        stats = manager.get_review_statistics()
        print("\nReview Statistics:")
        print(f"Total PRs Reviewed: {stats['total_prs_reviewed']}")
        print("\nAgent Statistics:")
        for agent, agent_stats in stats['agent_stats'].items():
            print(f"\n{agent.title()} Agent:")
            for key, value in agent_stats.items():
                print(f"  {key}: {value}")
    else:
        # Conduct PR review
        manager.review_pr(args.pr)

if __name__ == "__main__":
    main()