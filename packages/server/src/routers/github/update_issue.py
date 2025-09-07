from fastapi import APIRouter, status

from src.api.github import UpdateIssueAction, UpdateIssueRequest, UpdateIssueResponse
from src.clients import get_firestore_client, get_github_client, get_secret_client

router = APIRouter()


@router.post("/update-issue", status_code=status.HTTP_200_OK)
async def update_issue_async(request: UpdateIssueRequest) -> UpdateIssueResponse:
    """
    Update a GitHub issue from an Async task on behalf of the user.
    Supports three actions:
    - CLOSE_AS_COMPLETE: Close the GitHub issue as completed
    - DELETE: Close the GitHub issue as not planned
    - UPDATE_BODY: Update the issue body
    """
    firestore_client = get_firestore_client()
    task = await firestore_client.get_task_async(request.org_id, request.task_id)
    project = await firestore_client.get_project_async(request.org_id, task.project_id)
    access_token = await get_secret_client().get_user_github_token_async(request.user_id)
    github_client = get_github_client()

    if request.action == UpdateIssueAction.UPDATE_BODY:
        await github_client.update_issue_async(
            access_token=access_token,
            repo_full_name=project.repo,
            issue_number=task.github_issue_number,
            body=request.body,
        )
    else:
        await github_client.update_issue_async(
            access_token=access_token,
            repo_full_name=project.repo,
            issue_number=task.github_issue_number,
            state="closed",
            state_reason="completed" if request.action == UpdateIssueAction.CLOSE_AS_COMPLETE else "not_planned",
        )

    return UpdateIssueResponse()
