# cli.py

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
from llm.ollama_llm import OllamaLLM
from prompts.prompt_templates import create_review_prompt

def setup_logging():
    logging.basicConfig(level=LOG_LEVEL, format=LOG_FORMAT)
    return logging.getLogger(__name__)

logger = setup_logging()

def review_pr(pr_number=None):
    github_client = Github(GITHUB_TOKEN)
    repo = github_client.get_repo(REPO_NAME)
    llm = OllamaLLM()

    if pr_number:
        pull_requests = [repo.get_pull(pr_number)]
    else:
        pull_requests = get_open_pull_requests(repo)

    for pr in pull_requests:
        try:
            logger.info(f"Reviewing PR #{pr.number}: {pr.title}")
            diff = get_pull_request_diff(pr)
            if not diff:
                logger.warning(f"No diff found for PR #{pr.number}")
                continue

            previous_comments = get_previous_comments(pr)
            prompt = create_review_prompt(diff, previous_comments)
            review = llm.call(prompt)

            if not review.strip():
                logger.error(f"Empty review generated for PR #{pr.number}")
                continue

            post_review_comment(pr, review)
            logger.info(f"Review posted for PR #{pr.number}")
        except Exception as e:
            logger.error(f"Error processing PR #{pr.number}: {e}", exc_info=True)

def main():
    parser = argparse.ArgumentParser(description="AI-powered Pull Request Reviewer")
    parser.add_argument("--pr", type=int, help="PR number to review. If not provided, all open PRs will be reviewed.")
    args = parser.parse_args()

    review_pr(args.pr)

if __name__ == "__main__":
    main()