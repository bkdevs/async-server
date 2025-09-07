from fastapi import APIRouter, status

from src.api.github import CreatePullRequestRequest, CreatePullRequestResponse
from src.clients import get_firestore_client, get_github_client
from src.model.app.task import PullRequest

router = APIRouter()


@router.post("/create-pull-request", status_code=status.HTTP_200_OK)
async def create_pull_request_async(request: CreatePullRequestRequest) -> CreatePullRequestResponse:
    """
    Create a GitHub PR and update task with the created PR
    """
    firestore_client = get_firestore_client()
    org = await firestore_client.get_org_async(request.org_id)
    task = await firestore_client.get_task_async(org.id, request.task_id)
    project = await firestore_client.get_project_async(org.id, task.project_id)

    github_client = get_github_client()
    access_token = await github_client.generate_app_access_token_async(org.github_installation_id)
    pr_body = (
        f"{task.body}\n\n"
        f"## Requirements\n{task.get_requirements()}\n\n"
        f"Fixes #{task.github_issue_number}\n\n"
        "Generated with [Async](https://www.async.build)"
    )
    pull_request = await github_client.create_pull_request_async(
        access_token, project.repo, task.title, pr_body, request.branch_name, project.default_branch
    )
    await firestore_client.update_task_async(
        org.id,
        task.id,
        pull_request_url=pull_request.html_url,
        pull_request_branch=request.branch_name,
    )

    pull_request_doc = PullRequest(
        org_id=org.id,
        project_id=project.id,
        task_id=task.id,
        pull_request_url=pull_request.html_url,
    )
    await firestore_client.create_pull_request_async(pull_request_doc)
    return CreatePullRequestResponse()
