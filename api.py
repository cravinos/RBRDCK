import asyncio
from typing import List, Dict, Any
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import logging
from llm.ollama_llm import OllamaLLM
from config import GITHUB_TOKEN, REPO_OWNER, GITHUB_API_URL, FRONTEND_URL, LOG_LEVEL, LOG_FORMAT
from github_client import GithubClient
import httpx

app = FastAPI()
# REPO_OWNER is the username of the user using the app
# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize your language model
llm = OllamaLLM()

# Set up logging
logging.basicConfig(level=LOG_LEVEL, format=LOG_FORMAT)
logger = logging.getLogger(__name__)

@app.on_event("startup")
async def startup_event():
    app.state.http_client = httpx.AsyncClient()

@app.on_event("shutdown")
async def shutdown_event():
    await app.state.http_client.aclose()

# Pydantic Models
class RepositoryModel(BaseModel):
    name: str
    url: str

class PullRequestModel(BaseModel):
    number: int
    title: str

class RepoPullRequestsModel(BaseModel):
    repo_name: str
    pull_requests: List[PullRequestModel]

class OrganizationModel(BaseModel):
    org_name: str
    org_url: str

class ReviewResponseModel(BaseModel):
    review: str
    diff: str

class CliReviewResponseModel(BaseModel):
    message: str
    output: str

# Dependency for GithubClient
def get_github_client():
    return GithubClient()

# Helper Functions
async def get_user_repos(client: GithubClient) -> List[RepositoryModel]:
    try:
        logger.info(f"Fetching repositories for user: {REPO_OWNER}")
        repos = await client.get_user_repos()
        logger.info(f"Fetched {len(repos)} repositories for user: {REPO_OWNER}")
        return [RepositoryModel(name=repo["name"], url=repo["html_url"]) for repo in repos]
    except Exception as e:
        logger.error(f"Error fetching repos for user {REPO_OWNER}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

async def get_orgs(client: GithubClient) -> List[OrganizationModel]:
    try:
        logger.info(f"Fetching organizations for user: {REPO_OWNER}")
        orgs = await client.get_user_organizations()
        logger.info(f"Fetched {len(orgs)} organizations for user: {REPO_OWNER}")
        return [OrganizationModel(org_name=org["login"], org_url=org["url"]) for org in orgs]
    except Exception as e:
        logger.error(f"Error fetching orgs for user {REPO_OWNER}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

async def get_repo_pull_requests(client: GithubClient, repo_name: str) -> RepoPullRequestsModel:
    try:
        logger.info(f"Fetching open pull requests for repo: {repo_name}")
        prs = await client.get_repo_pull_requests(repo_name)
        pull_requests = [PullRequestModel(number=pr["number"], title=pr["title"]) for pr in prs]
        logger.info(f"Fetched {len(pull_requests)} open PRs for repo: {repo_name}")
        return RepoPullRequestsModel(repo_name=repo_name, pull_requests=pull_requests)
    except Exception as e:
        logger.error(f"Error fetching pull requests for repo {repo_name}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

async def get_pr_diff(client: GithubClient, repo_name: str, pr_number: int) -> str:
    try:
        logger.info(f"Fetching diff for PR #{pr_number} in repo: {repo_name}")
        diff = await client.get_pull_request_diff(repo_name, pr_number)
        logger.info(f"Fetched diff for PR #{pr_number} in repo: {repo_name}")
        return diff
    except Exception as e:
        logger.error(f"Error fetching diff for PR #{pr_number} in repo {repo_name}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

async def generate_pr_review(llm: OllamaLLM, diff: str) -> str:
    try:
        logger.info("Generating review using LLM")
        # Use the 'call' method instead of 'generate_review'
        review = await llm.call(diff)
        logger.info("Generated review using LLM")
        return review
    except Exception as e:
        logger.error(f"Error generating PR review: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

# API Endpoints
@app.get("/repos/", response_model=Dict[str, List[RepositoryModel]])
async def read_repos(client: GithubClient = Depends(get_github_client)) -> Dict[str, List[RepositoryModel]]:
    """Fetch all repositories for the authenticated user."""
    repos = await get_user_repos(client)
    return {"repositories": repos}

@app.get("/repo_pull_requests/{repo_name}", response_model=RepoPullRequestsModel)
async def get_repo_pull_requests_endpoint(repo_name: str, client: GithubClient = Depends(get_github_client)) -> RepoPullRequestsModel:
    """Fetch open pull requests for a specific repository."""
    return await get_repo_pull_requests(client, repo_name)

@app.get("/user_groups", response_model=Dict[str, List[OrganizationModel]])
async def get_user_groups(client: GithubClient = Depends(get_github_client)) -> Dict[str, List[OrganizationModel]]:
    """Fetch all organizations (groups) for the specified user."""
    orgs = await get_orgs(client)
    return {"organizations": orgs}

@app.get("/org_pull_requests/{org_name}", response_model=Dict[str, List[Dict[str, Any]]])
async def get_org_pull_requests_endpoint(org_name: str, client: GithubClient = Depends(get_github_client)) -> Dict[str, List[Dict[str, Any]]]:
    """Fetch open pull requests for all repositories in a specific organization."""
    try:
        repos = await client.get_org_repos(org_name)
        tasks = [get_repo_pull_requests(client, repo["name"]) for repo in repos]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        org_prs = [result.dict() for result in results if isinstance(result, RepoPullRequestsModel) and result.pull_requests]
        return {"repo_prs": org_prs}
    except Exception as e:
        logger.error(f"Error fetching pull requests for organization {org_name}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/run_cli_review/{pr_number}")
async def run_cli_review(pr_number: int) -> Dict[str, str]:
    try:
        output = github_client.run_cli_review(pr_number)
        return {"message": f"Review for PR #{pr_number} executed successfully", "output": output}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error running CLI review: {str(e)}")

# New Endpoint for Reviewing a Pull Request
@app.get("/review_pr/{repo_name}/{pr_number}", response_model=ReviewResponseModel)
async def review_pr_endpoint(repo_name: str, pr_number: int, client: GithubClient = Depends(get_github_client)) -> ReviewResponseModel:
    """Generate a review for a specific pull request using LLM."""
    try:
        # Fetch the diff for the pull request
        diff = await get_pr_diff(client, repo_name, pr_number)
        if not diff:
            raise HTTPException(status_code=404, detail="Diff not found for the specified pull request.")

        # Generate the review using the LLM
        review = await generate_pr_review(llm, diff)
        if not review:
            raise HTTPException(status_code=500, detail="Failed to generate review.")

        return ReviewResponseModel(review=review, diff=diff)
    except HTTPException as http_exc:
        logger.error(f"HTTP error occurred: {http_exc.detail}")
        raise http_exc
    except Exception as e:
        logger.error(f"Error reviewing PR #{pr_number} in repo {repo_name}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
