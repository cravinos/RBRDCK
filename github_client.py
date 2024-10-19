import requests
from config import GITHUB_TOKEN, REPO_USER

class GithubClient:
    def __init__(self):
        self.headers = {
            "Authorization": f"token {GITHUB_TOKEN}",
            "Accept": "application/vnd.github.v3+json"
        }
        self.base_url = "https://api.github.com"

    def get_open_pull_requests(self, repo_name):
        url = f"{self.base_url}/repos/{REPO_USER}/{repo_name}/pulls"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()

    def get_user_organizations(self):
        url = f"{self.base_url}/user/orgs"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()

    def get_user_repos(self):
        url = f"{self.base_url}/user/repos"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()

    def get_repo_pull_requests(self, repo_name):
        url = f"{self.base_url}/repos/{REPO_USER}/{repo_name}/pulls"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()

    def get_pull_request(self, repo_name, pr_number):
        url = f"{self.base_url}/repos/{REPO_USER}/{repo_name}/pulls/{pr_number}"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()

    def get_pull_request_diff(self, pr):
        response = requests.get(pr["diff_url"], headers=self.headers)
        response.raise_for_status()
        return response.text

    def generate_review(self, diff):
        # Implement your review generation logic here
        return "This is a placeholder review."

    def post_review_comment(self, pr, review):
        url = f"{self.base_url}/repos/{REPO_USER}/{pr['base']['repo']['name']}/issues/{pr['number']}/comments"
        data = {"body": review}
        response = requests.post(url, headers=self.headers, json=data)
        response.raise_for_status()
        return response.json()

    def run_cli_review(self, pr_number):
        # Implement your CLI review logic here
        return f"CLI review for PR #{pr_number} completed."