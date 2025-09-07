from fastapi import APIRouter, status

from src.api.github import CreateIssueRequest, CreateIssueResponse
from src.clients import get_firestore_client, get_github_client, get_secret_client

router = APIRouter()


@router.post("/create-issue", status_code=status.HTTP_200_OK)
async def create_issue_async(request: CreateIssueRequest) -> CreateIssueResponse:
    """
    Create a GitHub issue from an Async task on behalf of the user
    """
    firestore_client = get_firestore_client()
    user = await firestore_client.get_user_async(request.user_id)
    task = await firestore_client.get_task_async(request.org_id, request.task_id)
    project = await firestore_client.get_project_async(request.org_id, task.project_id)
    access_token = await get_secret_client().get_user_github_token_async(request.user_id)
    issue = await get_github_client().create_issue_async(
        access_token, project.repo, task.title, task.body, user.github_login
    )
    await firestore_client.update_task_async(
        request.org_id, task.id, github_issue_id=issue.id, github_issue_number=issue.number
    )
    return CreateIssueResponse()
