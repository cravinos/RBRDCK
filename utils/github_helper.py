# utils/github_helper.py

import requests
from github.Repository import Repository
from github.PullRequest import PullRequest
import logging
from config import GITHUB_TOKEN

logger = logging.getLogger(__name__)

def get_open_pull_requests(repo: Repository):
    try:
        pulls = repo.get_pulls(state='open', sort='created')
        return list(pulls)
    except Exception as e:
        logger.error(f"Error fetching pull requests: {e}")
        return []

def get_pull_request_diff(pr: PullRequest):
    try:
        headers = {
            'Accept': 'application/vnd.github.v3.diff',
            'Authorization': f'token {GITHUB_TOKEN}'
        }
        response = requests.get(pr.diff_url, headers=headers)
        response.raise_for_status()
        return response.text
    except Exception as e:
        logger.error(f"Error fetching diff for PR #{pr.number}: {e}")
        return ""

def post_review_comment(pr: PullRequest, review: str):
    try:
        pr.create_issue_comment(review)
    except Exception as e:
        logger.error(f"Error posting review for PR #{pr.number}: {e}")
