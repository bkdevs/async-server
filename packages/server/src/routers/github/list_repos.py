from fastapi import APIRouter, status

from src.api.github import ListReposRequest, ListReposResponse
from src.clients import get_firestore_client, get_github_client

router = APIRouter()


@router.post("/list-repos", status_code=status.HTTP_200_OK)
async def list_repos_async(request: ListReposRequest) -> ListReposResponse:
    org = await get_firestore_client().get_org_async(request.org_id)

    repos = []
    github_client = get_github_client()
    access_token = await github_client.generate_app_access_token_async(org.github_installation_id)
    async for repo in github_client.list_installation_repos_async(access_token):
        repos.append(repo)
    repos.sort(key=lambda repo: repo.updated_at, reverse=True)
    return ListReposResponse(repos=repos)
