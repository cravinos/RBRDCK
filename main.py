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
from prompts.prompt_templates import (
    create_review_prompt,
    create_documentation_review_prompt
)
from agents.documentation_review_agent import DocumentationReviewAgent

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

def setup_agents():
    llm = OllamaLLM()
    documentation_agent = DocumentationReviewAgent()
    return llm, documentation_agent

def perform_code_review(pr, diff, previous_comments, llm):
    code_review_prompt = create_review_prompt(diff, previous_comments)
    code_review = llm.call(code_review_prompt)
    if code_review.strip():
        post_review_comment(pr, f"**Code Review:**\n\n{code_review}")
        logger.info(f"Posted code review for PR #{pr.number}")
    else:
        logger.warning(f"No code review generated for PR #{pr.number}")

def perform_documentation_review(pr, diff, previous_comments, documentation_agent):
    documentation_review = documentation_agent.review_documentation(diff, previous_comments)
    if documentation_review.strip():
        post_review_comment(pr, f"**Documentation Review:**\n\n{documentation_review}")
        logger.info(f"Posted documentation review for PR #{pr.number}")
    else:
        logger.warning(f"No documentation review generated for PR #{pr.number}")

def review_pr(pr_number=None, review_docs=False):
    github_client = Github(GITHUB_TOKEN)
    repo = github_client.get_repo(REPO_NAME)
    llm, documentation_agent = setup_agents()

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

            # Fetch previous comments
            previous_comments = get_previous_comments(pr)
            logger.debug(f"Fetched previous comments for PR #{pr.number}")

            # Perform Code Review
            perform_code_review(pr, diff, previous_comments, llm)

            # Perform Documentation Review if enabled
            if review_docs:
                perform_documentation_review(pr, diff, previous_comments, documentation_agent)

        except Exception as e:
            logger.error(f"Error processing PR #{pr.number}: {e}", exc_info=True)

def main():
    parser = argparse.ArgumentParser(description="AI-powered Pull Request Reviewer")
    parser.add_argument("--pr", type=int, help="PR number to review. If not provided, all open PRs will be reviewed.")
    parser.add_argument("--review-docs", action="store_true", help="Enable documentation review")
    args = parser.parse_args()

    review_pr(args.pr, args.review_docs)

if __name__ == "__main__":
    main()
