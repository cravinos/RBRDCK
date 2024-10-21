# cli.py

import argparse
from utils.github_helper import (
    get_previous_comments,
    get_pull_request_diff,
    generate_review,
    post_review_comment
)
from config import REPO_OWNER, GITHUB_TOKEN  # Ensure these are correctly defined

def main():
    parser = argparse.ArgumentParser(description="Run CLI review for a GitHub PR.")
    parser.add_argument('--repo', type=str, required=True, help='Repository name')
    parser.add_argument('--pr', type=int, required=True, help='Pull Request number')
    args = parser.parse_args()

    repo_name = args.repo
    pr_number = args.pr

    try:
        # Fetch previous comments
        comments = get_previous_comments(repo_name, pr_number)

        # Fetch PR diff
        diff = get_pull_request_diff(repo_name, pr_number)

        # Generate review using LLM
        review = generate_review(diff)

        # Post review comment
        post_review_comment(repo_name, pr_number, review)

        print("CLI review executed successfully.")
    except Exception as e:
        print(f"Error running CLI review: {e}")

if __name__ == "__main__":
    main()
