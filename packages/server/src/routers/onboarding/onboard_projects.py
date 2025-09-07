from fastapi import APIRouter, status

from src.api.onboarding import OnboardProjectsRequest, OnboardProjectsResponse
from src.clients import get_async_client, get_firestore_client
from src.model.app.project import Project
from src.model.app.project import Repository as AsyncRepository
from src.model.github import Repository

router = APIRouter()


@router.post("/onboard-projects", status_code=status.HTTP_200_OK)
async def onboard_projects_async(request: OnboardProjectsRequest) -> OnboardProjectsResponse:
    for repo in request.repos:
        project = await _create_project_async(request.org_id, repo)
        await _create_repository_async(request.org_id, project)
        await get_async_client().invoke_index_project_job_async(request.org_id, project.id, request.is_dev)

    await get_firestore_client().update_org_async(request.org_id, onboarded=True)
    return OnboardProjectsResponse()


async def _create_project_async(org_id: str, repo: Repository) -> Project:
    project = Project(
        name=repo.name,
        repo=repo.full_name,
        description=repo.description or "",
        default_branch=repo.default_branch,
    )
    return await get_firestore_client().create_project_async(org_id, project)


async def _create_repository_async(org_id: str, project: Project):
    repository = AsyncRepository(
        full_name=project.repo,
        org_id=org_id,
        project_id=project.id,
    )
    await get_firestore_client().create_repository_async(repository)
