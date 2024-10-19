from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from github_client import GithubClient
from config import REPO_NAME, REPO_USER
from typing import List, Dict, Any

app = FastAPI()
github_client = GithubClient()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/open_prs")
async def get_open_prs() -> List[Dict[str, Any]]:
    try:
        prs = github_client.get_open_pull_requests(REPO_NAME)
        return [{"number": pr["number"], "title": pr["title"]} for pr in prs]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching open pull requests: {str(e)}")

@app.get("/user_groups")
async def get_user_groups() -> Dict[str, List[Dict[str, str]]]:
    try:
        orgs = github_client.get_user_organizations()
        return {"organizations": [{"org_name": org["login"], "org_url": org["url"]} for org in orgs]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching user groups: {str(e)}")

@app.get("/repos/")
async def get_repos() -> Dict[str, List[Dict[str, str]]]:
    try:
        repos = github_client.get_user_repos()
        return {"repositories": [{"name": repo["name"], "url": repo["html_url"]} for repo in repos]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching repositories: {str(e)}")

@app.get("/repo_pull_requests")
async def get_repo_pull_requests() -> Dict[str, List[Dict[str, Any]]]:
    try:
        repos = github_client.get_user_repos()
        repo_prs = []
        for repo in repos:
            pulls = github_client.get_repo_pull_requests(repo["name"])
            if pulls:
                repo_prs.append({
                    "repo_name": repo["name"],
                    "pull_requests": [{"number": pr["number"], "title": pr["title"]} for pr in pulls]
                })
        return {"repo_prs": repo_prs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching repository pull requests: {str(e)}")

@app.get("/repo_pull_requests/{repo_name}")
async def get_specific_repo_pull_requests(repo_name: str) -> Dict[str, Any]:
    try:
        pulls = github_client.get_repo_pull_requests(repo_name)
        return {
            "repo_name": repo_name,
            "pull_requests": [{"number": pr["number"], "title": pr["title"]} for pr in pulls]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching pull requests for repository {repo_name}: {str(e)}")

@app.get("/review_pr/{pr_number}")
async def review_pr(pr_number: int) -> Dict[str, str]:
    try:
        pr = github_client.get_pull_request(REPO_NAME, pr_number)
        if not pr:
            raise HTTPException(status_code=404, detail="Pull request not found")
        diff = github_client.get_pull_request_diff(pr)
        if not diff:
            raise HTTPException(status_code=404, detail="PR diff not found")
        review = github_client.generate_review(diff)
        if not review.strip():
            raise HTTPException(status_code=500, detail="Empty review generated")
        github_client.post_review_comment(pr, review)
        return {"review": review, "diff": diff}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reviewing pull request: {str(e)}")

@app.post("/run_cli_review/{pr_number}")
async def run_cli_review(pr_number: int) -> Dict[str, str]:
    try:
        output = github_client.run_cli_review(pr_number)
        return {"message": f"Review for PR #{pr_number} executed successfully", "output": output}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error running CLI review: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)