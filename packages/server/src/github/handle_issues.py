from src.clients import get_firestore_client
from src.model import compute_repository_doc_id
from src.model.app import User
from src.model.app.task import Task, TaskSource, TaskStatus
from src.model.github import Issue, IssuesEvent, IssuesEventAction


async def handle_issues_async(event: IssuesEvent):
    firestore_client = get_firestore_client()
    repository = await firestore_client.get_repository_async(compute_repository_doc_id(event.repository.full_name))
    if not repository:
        return

    task = await firestore_client.get_task_by_github_id_async(repository.org_id, event.issue.id)
    match event.action:
        case IssuesEventAction.OPENED:
            if task:
                # task is created from Async
                return
            await _handle_issue_opened_async(repository.org_id, repository.project_id, event.issue)
        case IssuesEventAction.EDITED:
            if not task:
                return
            await _handle_issue_edited_async(repository.org_id, task.id, event.issue)
        case IssuesEventAction.CLOSED:
            if not task:
                return
            await _handle_issue_closed_async(repository.org_id, task)
        case _:
            pass


async def _handle_issue_opened_async(org_id: str, project_id: str, issue: Issue):
    firestore_client = get_firestore_client()
    task = Task(
        title=issue.title,
        body=issue.body or "",
        author=issue.user.login,
        source=TaskSource.GITHUB,
        comments=[],
        github_issue_id=issue.id,
        github_issue_number=issue.number,
        project_id=project_id,
        created_at=issue.created_at,
    )
    await firestore_client.create_task_async(org_id, task)

    users = await firestore_client.get_users_in_org_async(org_id)
    for user in users:
        # for now, only subsribe the task if either it's created by the user or it's assigned to the user
        if not _is_created_by_user(user, issue) and not _is_assigned_to_user(user, issue):
            continue

        user.subscribed_tasks.append(task.id)
        await firestore_client.update_user_async(user.id, subscribed_tasks=user.subscribed_tasks)


async def _handle_issue_edited_async(org_id: str, task_id: str, issue: Issue):
    await get_firestore_client().update_task_async(org_id, task_id, title=issue.title, body=issue.body or "")


async def _handle_issue_closed_async(org_id: str, task: Task):
    firestore_client = get_firestore_client()
    if task.status != TaskStatus.COMPLETED:
        # if PR is merged via Async, task is already marked as completed
        await firestore_client.update_task_async(org_id, task.id, status=TaskStatus.COMPLETED)

    users = await firestore_client.get_users_in_org_async(org_id)
    for user in users:
        if task.id not in user.subscribed_tasks:
            continue

        # remove task from all users
        user.subscribed_tasks.remove(task.id)
        await firestore_client.update_user_async(user.id, subscribed_tasks=user.subscribed_tasks)


def _is_created_by_user(user: User, issue: Issue) -> bool:
    return user.github_id == issue.user.id


def _is_assigned_to_user(user: User, issue: Issue) -> bool:
    return issue.assignee and user.github_id == issue.assignee.id
