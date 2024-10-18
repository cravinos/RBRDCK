# main.py

import logging
import sys
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

# Configure logging to output to both console and file
def setup_logging():
    logger = logging.getLogger()
    logger.setLevel(LOG_LEVEL)

    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(LOG_LEVEL)
    console_formatter = logging.Formatter(LOG_FORMAT)
    console_handler.setFormatter(console_formatter)

    # Create file handler
    file_handler = logging.FileHandler('pr_reviewer.log')
    file_handler.setLevel(LOG_LEVEL)
    file_formatter = logging.Formatter(LOG_FORMAT)
    file_handler.setFormatter(file_formatter)

    # Add both handlers to the logger
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger

# Call setup_logging at the start of your script
logger = setup_logging()

def main():
    # Initialize GitHub client
    github_client = Github(GITHUB_TOKEN)
    repo = github_client.get_repo(REPO_NAME)

    # Get open pull requests
    pull_requests = get_open_pull_requests(repo)
    if not pull_requests:
        logger.info("No open pull requests found.")
        return

    # Initialize LLM
    llm = OllamaLLM()

    for pr in pull_requests:
        try:
            logger.info(f"Reviewing PR #{pr.number}: {pr.title}")
            diff = get_pull_request_diff(pr)
            if not diff:
                logger.warning(f"No diff found for PR #{pr.number}")
                continue

            # Fetch previous comments
            previous_comments = get_previous_comments(pr)
            logger.debug(f"Fetched previous comments for PR #{pr.number}")

            # Create prompt for LLM
            prompt = create_review_prompt(diff, previous_comments)
            logger.debug(f"Generated prompt for PR #{pr.number}: {prompt[:100]}...")  # Log the first 100 characters of the prompt

            # Get LLM's review
            review = llm.call(prompt)
            logger.debug(f"LLM Review for PR #{pr.number}: {review[:100]}...")  # Log the first 100 characters of the review

            if not review.strip():
                logger.error(f"Empty review generated for PR #{pr.number}")
                continue

            # Post review comment
            post_review_comment(pr, review)
        except Exception as e:
            logger.error(f"Error processing PR #{pr.number}: {e}", exc_info=True)

if __name__ == "__main__":
    main()