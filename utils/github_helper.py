# utils/github_helper.py

import requests
from github.Repository import Repository
from github.PullRequest import PullRequest
import logging
from config import GITHUB_TOKEN
from typing import List, Dict
import re

logger = logging.getLogger(__name__)

def get_open_pull_requests(repo):
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

def parse_review_comments(review_body: str) -> List[Dict]:
    """
    Parses the LLM's review and extracts individual comments with file paths and line numbers.
    """
    comments = []
    pattern = re.compile(
        r"- \*\*Issue Description\*\*\n\n(.+?)\n\n\*\*Suggestion:\*\*\n\n```suggestion\n(.+?)\n```\n\n\*\*File:\*\* `(.+?)`\n\n\*\*Line:\*\* (\d+)",
        re.DOTALL
    )
    matches = pattern.findall(review_body)
    for match in matches:
        issue_description, suggestion, file_path, line_number = match
        comments.append({
            'body': f"{issue_description}\n\n```suggestion\n{suggestion}\n```",
            'path': file_path,
            'line': int(line_number),
        })
    return comments

def post_review_comment(pr: PullRequest, review_body: str):
    try:
        if not review_body.strip():
            logger.error("Review body is empty. Skipping review post.")
            return

        comments_data = parse_review_comments(review_body)
        if comments_data:
            review_comments = []
            for comment in comments_data:
                position = get_diff_position(pr, comment['path'], comment['line'])
                if position is not None:
                    review_comments.append({
                        'path': comment['path'],
                        'position': position,
                        'body': comment['body'],
                    })
                else:
                    logger.warning(f"Could not find position for comment: {comment}")
            
            if review_comments:
                pr.create_review(
                    body="Please see the suggested changes below:",
                    event='COMMENT',
                    comments=review_comments,
                )
                logger.info(f"Posted review with {len(review_comments)} comments for PR #{pr.number}")
            else:
                logger.warning(f"No valid comments to post for PR #{pr.number}")
        else:
            # Fallback to a general comment if parsing fails, but ensure it's not empty
            if review_body.strip():
                pr.create_issue_comment(review_body)
                logger.info(f"Posted general comment for PR #{pr.number}")
            else:
                logger.warning(f"No content to post for PR #{pr.number}")
    except Exception as e:
        logger.error(f"Error posting review for PR #{pr.number}: {e}", exc_info=True)

def get_diff_position(pr: PullRequest, file_path: str, line_number: int) -> int:
    """
    Maps a line number in the file to a position in the diff.
    """
    try:
        files = pr.get_files()
        for file in files:
            if file.filename == file_path:
                patch = file.patch
                # Parse the patch to map line numbers to positions
                position = map_line_to_position(patch, line_number)
                if position:
                    return position
        logger.error(f"Could not find position for {file_path}:{line_number}")
        return None
    except Exception as e:
        logger.error(f"Error getting diff position: {e}")
        return None

def map_line_to_position(patch: str, line_number: int) -> int:
    """
    Parses the patch text to find the diff position of the given line number.
    """
    current_line = None
    position = 0
    for line in patch.split('\n'):
        if line.startswith('@@'):
            # Parse the hunk header to get the starting line number
            m = re.match(r'@@ \-\d+(?:,\d+)? \+(\d+)(?:,\d+)? @@', line)
            if m:
                current_line = int(m.group(1)) - 1
        elif line.startswith('+'):
            current_line += 1
            position += 1
            if current_line == line_number:
                return position
        elif not line.startswith('-'):
            current_line += 1
            position += 1
    return None
def get_previous_comments(pr: PullRequest) -> str:
    """
    Fetches previous comments on a pull request.
    
    Args:
    pr (PullRequest): The pull request object.
    
    Returns:
    str: A formatted string containing previous comments.
    """
    comments = pr.get_issue_comments()
    formatted_comments = []
    for comment in comments:
        formatted_comments.append(f"Commenter: {comment.user.login}\nComment: {comment.body}\n")
    
    return "\n".join(formatted_comments)