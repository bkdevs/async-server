from fastapi import APIRouter, BackgroundTasks, status

from src.api.github import ImportIssuesRequest, ImportIssuesResponse
from src.clients import get_firestore_client, get_github_client
from src.model.app import Org
from src.model.app.project import Project
from src.model.app.task import Task, TaskComment, TaskSource

router = APIRouter()


@router.post("/import-issues", status_code=status.HTTP_200_OK)
async def import_issues_async(request: ImportIssuesRequest, background_tasks: BackgroundTasks) -> ImportIssuesResponse:
    firestore_client = get_firestore_client()
    org = await firestore_client.get_org_async(request.org_id)
    projects = await firestore_client.get_projects_async(org.id)
    for project in projects:
        background_tasks.add_task(_process_repository_issues_async, request.user_id, org, project)
    return ImportIssuesResponse()


async def _process_repository_issues_async(user_id: str, org: Org, project: Project):
    firestore_client = get_firestore_client()
    github_client = get_github_client()
    access_token = await github_client.generate_app_access_token_async(org.github_installation_id)

    async for github_issue in github_client.list_repository_open_issues_async(access_token, project.repo):
        task_comments = []
        async for github_issue_comment in github_client.list_issue_comments_async(
            access_token, project.repo, github_issue.number
        ):
            task_comments.append(
                TaskComment(
                    id=github_issue_comment.id,
                    author=github_issue_comment.user.login,
                    body=github_issue_comment.body,
                    created_at=github_issue_comment.created_at,
                )
            )
        task = Task(
            title=github_issue.title,
            body=github_issue.body or "",
            author=github_issue.user.login,
            source=TaskSource.GITHUB,
            comments=task_comments,
            github_issue_id=github_issue.id,
            github_issue_number=github_issue.number,
            project_id=project.id,
            created_at=github_issue.created_at,
        )
        await firestore_client.create_task_async(org.id, task)

        # Auto subscribe each task to the user as it's created
        # Uses ArrayUnion to safely append without race conditions
        await firestore_client.add_user_subscribed_task_async(user_id, task.id)
