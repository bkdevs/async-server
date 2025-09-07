from fastapi import APIRouter, status

from src.api.github import CreateIssueCommentRequest, CreateIssueCommentResponse
from src.clients import get_firestore_client, get_github_client, get_secret_client

router = APIRouter()


@router.post("/create-issue-comment", status_code=status.HTTP_200_OK)
async def create_issue_comment_async(request: CreateIssueCommentRequest) -> CreateIssueCommentResponse:
    """
    Create a comment on a GitHub issue from an Async task on behalf of the user
    """
    firestore_client = get_firestore_client()
    task = await firestore_client.get_task_async(request.org_id, request.task_id)
    project = await firestore_client.get_project_async(request.org_id, task.project_id)
    access_token = await get_secret_client().get_user_github_token_async(request.user_id)
    comment = await get_github_client().create_issue_comment_async(
        access_token, project.repo, task.github_issue_number, request.comment_body
    )
    return CreateIssueCommentResponse(comment_id=comment.id)
