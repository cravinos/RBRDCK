import os
import httpx
from typing import List, Optional
from httpx import AsyncClient, Response

# Assuming GITHUB_TOKEN and REPO_OWNER are set in environment or config
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
REPO_OWNER = os.getenv('REPO_OWNER', 'default_owner')

class GithubAPI:
    def __init__(self):
        self.client = AsyncClient(
            headers={
                "Authorization": f"token {GITHUB_TOKEN}",
                "Accept": "application/vnd.github.v3+json",
            },
            base_url=f"https://api.github.com/repos/{REPO_OWNER}/"
        )

    async def get_previous_comments(self, repo_name: str, pr_number: int) -> List[str]:
        """Fetch previous comments from a pull request with pagination."""
        url = f"{repo_name}/issues/{pr_number}/comments"
        comments = []
        page = 1
        try:
            while True:
                params = {'page': page}
                response = await self.client.get(url, params=params)
                response.raise_for_status()
                page_comments = response.json()
                if not page_comments:
                    break
                comments.extend(comment["body"] for comment in page_comments)
                page += 1
                if 'X-RateLimit-Remaining' in response.headers and int(response.headers['X-RateLimit-Remaining']) == 0:
                    print("Approaching rate limit.")
                    break
        except httpx.HTTPStatusError as e:
            print(f"HTTP error occurred: {e}")
        except httpx.RequestError as e:
            print(f"An error occurred while requesting: {e}")
        return comments

    async def get_pull_request_diff(self, repo_name: str, pr_number: int) -> str:
        """Fetch the diff of a pull request."""
        url = f"{repo_name}/pulls/{pr_number}"
        self.client.headers["Accept"] = "application/vnd.github.v3.diff"
        try:
            response = await self.client.get(url)
            response.raise_for_status()
            return response.text
        except httpx.HTTPStatusError as e:
            print(f"Failed to fetch PR diff: {e}")
            return ""
        finally:
            self.client.headers["Accept"] = "application/vnd.github.v3+json"

    async def generate_review(self, diff: str) -> str:
        """Generate a review for the given diff. Placeholder for LLM logic."""
        return "Review placeholder: Consider code formatting."

    async def post_review_comment(self, repo_name: str, pr_number: int, comment: str):
        """Post a review comment to a pull request."""
        url = f"{repo_name}/issues/{pr_number}/comments"
        try:
            response = await self.client.post(url, json={"body": comment})
            response.raise_for_status()
            print("Review comment posted successfully.")
        except httpx.HTTPStatusError as e:
            print(f"Failed to post review comment: {e}")

    async def __aexit__(self, exc_type, exc, tb):
        await self.client.aclose()

# Usage example (in an async context):
# async def main():
#     github_api = GithubAPI()
#     comments = await github_api.get_previous_comments('repoName', 123)
#     print(comments)
# asyncio.run(main())