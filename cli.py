# cli.py
from typing import Dict, List, Optional
import argparse
import logging
from github import Github
from config import GITHUB_TOKEN, LOG_FORMAT, LOG_LEVEL
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
    
    def __init__(self, repo_user: str, repo_name: str):
        if not GITHUB_TOKEN:
            raise ValueError("GitHub token not found. Please set GITHUB_TOKEN in .env file")
            
        self.github_client = Github(GITHUB_TOKEN)
        self.repo = self.github_client.get_repo(f"{repo_user}/{repo_name}")
        self.orchestrator = ReviewOrchestrator()

    def review_pr(self, pr_number: Optional[int] = None) -> Dict:
        """
        Reviews pull requests using a collaborative approach among review agents.
        
        Args:
            pr_number: Optional PR number to review. If not provided, reviews all open PRs.
            
        Returns:
            Dict containing review results and status
        """
        result = {
            'status': 'success',
            'reviews': [],
            'error': None
        }

        try:
            # Get pull requests to review
            if pr_number:
                pull_requests = [self.repo.get_pull(pr_number)]
                logger.info(f"Reviewing PR #{pr_number}")
            else:
                pull_requests = get_open_pull_requests(self.repo)

            if not pull_requests:
                result['status'] = 'no_prs'
                return result

            for pr in pull_requests:
                pr_result = {
                    'pr_number': pr.number,
                    'title': pr.title,
                    'status': 'success',
                    'review': None,
                    'error': None
                }

                try:
                    logger.info(f"Reviewing PR #{pr.number}: {pr.title}")
                    
                    diff = get_pull_request_diff(pr)
                    if not diff:
                        pr_result['status'] = 'error'
                        pr_result['error'] = 'No diff found'
                        continue

                    previous_comments = get_previous_comments(pr)
                    review_context = ReviewContext(pr, diff, previous_comments)

                    final_review = self.orchestrator.conduct_collaborative_review(review_context)
                    
                    if final_review.strip():
                        post_review_comment(pr, final_review)
                        pr_result['review'] = final_review
                        logger.info(f"Posted review for PR #{pr.number}")
                    else:
                        pr_result['status'] = 'error'
                        pr_result['error'] = 'Empty review generated'
                        
                except Exception as e:
                    pr_result['status'] = 'error'
                    pr_result['error'] = str(e)
                    logger.error(f"Error reviewing PR #{pr.number}: {e}")

                result['reviews'].append(pr_result)

        except Exception as e:
            result['status'] = 'error'
            result['error'] = str(e)
            logger.error(f"Error in review process: {e}")

        return result

    def get_review_statistics(self) -> Dict:
        """Gets statistics about the review process."""
        return {
            'repository': self.repo.full_name,
            'total_prs_reviewed': len(list(get_open_pull_requests(self.repo))),
            'agent_stats': self.orchestrator.get_agent_statistics()
        }

def run_review(repo_user: str, repo_name: str, pr_number: Optional[int] = None, stats: bool = False) -> Dict:
    """
    Main function to run the review process, can be called from API or CLI.
    
    Args:
        repo_user: GitHub username or organization
        repo_name: Repository name
        pr_number: Optional PR number to review
        stats: Whether to return statistics instead of running review
        
    Returns:
        Dict containing results or statistics
    """
    try:
        manager = ReviewManager(repo_user=repo_user, repo_name=repo_name)
        
        if stats:
            return {'type': 'stats', 'data': manager.get_review_statistics()}
        else:
            return {'type': 'review', 'data': manager.review_pr(pr_number)}
            
    except Exception as e:
        return {
            'type': 'error',
            'error': str(e)
        }

def main():
    parser = argparse.ArgumentParser(
        description="AI-powered Pull Request Reviewer",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  Review specific PR:
    python cli.py username repo-name --pr 123
    
  Review all open PRs:
    python cli.py username repo-name
    
  Show statistics:
    python cli.py username repo-name --stats
        """
    )
    
    parser.add_argument(
        "repo_user",
        help="GitHub username or organization"
    )
    parser.add_argument(
        "repo_name",
        help="Repository name"
    )
    parser.add_argument(
        "--pr", 
        type=int, 
        help="PR number to review. If not provided, all open PRs will be reviewed"
    )
    parser.add_argument(
        "--stats",
        action="store_true",
        help="Show review statistics"
    )
    args = parser.parse_args()

    result = run_review(
        repo_user=args.repo_user,
        repo_name=args.repo_name,
        pr_number=args.pr,
        stats=args.stats
    )

    # Pretty print results
    if result['type'] == 'stats':
        stats = result['data']
        print("\nReview Statistics:")
        print(f"Repository: {stats['repository']}")
        print(f"Total PRs Reviewed: {stats['total_prs_reviewed']}")
        print("\nAgent Statistics:")
        for agent, agent_stats in stats['agent_stats'].items():
            print(f"\n{agent.title()} Agent:")
            for key, value in agent_stats.items():
                print(f"  {key}: {value}")
    elif result['type'] == 'error':
        print(f"\nError: {result['error']}")

if __name__ == "__main__":
    main()