# main.py

import logging
from github import Github
from config import GITHUB_TOKEN, REPO_NAME, LOG_FORMAT, LOG_LEVEL
from utils.github_helper import (
    get_open_pull_requests,
    get_pull_request_diff,
    post_review_comment
)
from llm.ollama_llm import OllamaLLM
from prompts.prompt_templates import create_review_prompt

# Configure logging
logging.basicConfig(level=LOG_LEVEL, format=LOG_FORMAT)
logger = logging.getLogger(__name__)

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
        logger.info(f"Reviewing PR #{pr.number}: {pr.title}")
        diff = get_pull_request_diff(pr)
        if not diff:
            logger.warning(f"No diff found for PR #{pr.number}")
            continue

        # Create prompt for LLM
        prompt = create_review_prompt(diff)

        # Get LLM's review
        review = llm.call(prompt)

        # Post review comment
        post_review_comment(pr, review)
        logger.info(f"Posted review for PR #{pr.number}")

if __name__ == "__main__":
    main()
