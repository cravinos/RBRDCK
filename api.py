import subprocess
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from llm.ollama_llm import OllamaLLM
from utils.github_helper import get_open_pull_requests, get_pull_request_diff, post_review_comment
from github import Github
from config import GITHUB_TOKEN, REPO_NAME, REPO_USER  # Make sure REPO_USER is properly imported


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this as needed for your security requirements
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Initialize GitHub and LLM clients
github_client = Github(GITHUB_TOKEN)
repo = github_client.get_repo(REPO_NAME)
llm = OllamaLLM()

@app.get("/review_pr/{pr_number}")
async def review_pr(pr_number: int):
    try:
        pr = repo.get_pull(pr_number)
        diff = get_pull_request_diff(pr)
        if not diff:
            raise HTTPException(status_code=404, detail="PR diff not found")
        review = llm.call(f"Review this diff: {diff}")
        if not review.strip():
            raise HTTPException(status_code=500, detail="Empty review generated")
        post_review_comment(pr, review)
        return {"review": review}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/open_prs")
async def open_prs():
    try:
        pull_requests = get_open_pull_requests(repo)
        pr_data = [{"number": pr.number, "title": pr.title} for pr in pull_requests]
        print(pr_data)  # Debugging: Print the response data
        return pr_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/projects")
async def get_user_projects():
    try:
        # Fetch the user based on REPO_USER instead of REPO_NAME
        user = github_client.get_user(REPO_USER)
        repos = user.get_repos()  # Get all repositories for the user
        project_list = [{"name": repo.name, "url": repo.html_url} for repo in repos]
        return {"projects": project_list}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching user projects: {str(e)}")

@app.post("/run_cli_review/{pr_number}")
async def run_cli_review(pr_number: int):
    try:
        # Run the CLI command for the specified PR number
        result = subprocess.run(
            ["python", "cli.py", "--pr", str(pr_number)], 
            capture_output=True, 
            text=True
        )
        # Check for errors
        if result.returncode != 0:
            raise HTTPException(status_code=500, detail=f"CLI command failed: {result.stderr}")
        
        return {"message": f"Review for PR #{pr_number} executed successfully", "output": result.stdout}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error running CLI command: {str(e)}")

@app.get("/repo_pull_requests")
async def get_repo_pull_requests():
    try:
        # Fetch the repositories for the REPO_USER
        user = github_client.get_user(REPO_USER)
        repos = user.get_repos()

        repo_prs = []
        # Loop through each repository and get its open pull requests
        for repo in repos:
            pulls = repo.get_pulls(state='open', sort='created')
            if pulls.totalCount > 0:
                repo_prs.append({
                    "repo_name": repo.name,
                    "pull_requests": [
                        {"number": pr.number, "title": pr.title} for pr in pulls
                    ]
                })

        return {"repo_prs": repo_prs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching repositories and pull requests: {str(e)}")

@app.get("/user_groups")
async def get_user_groups():
    try:
        # Fetch the organizations for the REPO_USER
        user = github_client.get_user(REPO_USER)
        organizations = user.get_orgs()

        orgs_data = [{"org_name": org.login, "org_url": org.html_url} for org in organizations]
        return {"organizations": orgs_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching user groups: {str(e)}")


@app.get("/org_pull_requests/{org_name}")
async def get_org_pull_requests(org_name: str):
    try:
        org = github_client.get_organization(org_name)
        repos = org.get_repos()

        org_prs = []
        for repo in repos:
            pulls = repo.get_pulls(state='open', sort='created')
            if pulls.totalCount > 0:
                org_prs.append({
                    "repo_name": repo.name,
                    "pull_requests": [
                        {"number": pr.number, "title": pr.title} for pr in pulls
                    ]
                })

        return {"repo_prs": org_prs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching pull requests for organization: {str(e)}")
