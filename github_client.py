import httpx  # Add this line
from httpx import AsyncClient
from config import GITHUB_TOKEN, REPO_USER

class GithubClient:
    def __init__(self):
        self.headers = {
            "Authorization": f"token {GITHUB_TOKEN}",
            "Accept": "application/vnd.github.v3+json"
        }
        self.base_url = "https://api.github.com"
        self.client = AsyncClient(headers=self.headers, base_url=self.base_url)  # Remove 'httpx.'

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.client.aclose()

    async def _get_request(self, url: str) -> dict:
        async with AsyncClient() as client:  # Remove 'httpx.'
            response = await client.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()

    async def get_user_repos(self):
        url = f"{self.base_url}/users/{REPO_USER}/repos"
        return await self._get_request(url)

    async def get_open_pull_requests(self, repo_name):
        url = f"{self.base_url}/users/{REPO_USER}/repos/{repo_name}/pulls"
        return await self._get_request(url)

    async def get_repo_pull_requests(self, repo_name):
        url = f"{self.base_url}/repos/{REPO_USER}/{repo_name}/pulls"
        return await self._get_request(url)

    async def get_user_organizations(self):
        url = f"{self.base_url}/user/orgs"
        return await self._get_request(url)

    async def get_pull_request(self, repo_name: str, pr_number: int) -> dict:
        url = f"{self.base_url}/repos/{REPO_USER}/{repo_name}/pulls/{pr_number}"
        return await self._get_request(url)
    
    # ... (other methods remain unchanged)

    async def get_pull_request_diff(self, repo_name: str, pr_number: int) -> str:
        """Fetch the diff of a pull request."""
        url = f"{self.base_url}/repos/{REPO_USER}/{repo_name}/pulls/{pr_number}"
        self.client.headers["Accept"] = "application/vnd.github.v3.diff"
        try:
            response = await self.client.get(url)
            response.raise_for_status()
            return response.text
        except httpx.HTTPStatusError as e:
            logger.error(f"Failed to fetch PR diff: {e}")
            return ""
        finally:
            self.client.headers["Accept"] = "application/vnd.github.v3+json"
