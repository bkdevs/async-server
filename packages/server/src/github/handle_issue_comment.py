from src.clients import get_firestore_client
from src.model import compute_repository_doc_id
from src.model.app.task import Task, TaskComment
from src.model.github import IssueComment, IssueCommentEvent, IssueCommentEventAction


async def handle_issue_comment_async(event: IssueCommentEvent):
    firestore_client = get_firestore_client()
    repository = await firestore_client.get_repository_async(compute_repository_doc_id(event.repository.full_name))
    if not repository:
        return

    task = await firestore_client.get_task_by_github_id_async(repository.org_id, event.issue.id)
    if not task:
        return

    match event.action:
        case IssueCommentEventAction.CREATED:
            await _handle_issue_comment_created_async(repository.org_id, task, event.comment)
        case IssueCommentEventAction.EDITED:
            await _handle_issue_comment_edited_async(repository.org_id, task, event.comment)
        case IssueCommentEventAction.DELETED:
            await _handle_issue_comment_deleted_async(repository.org_id, task, event.comment)


async def _handle_issue_comment_created_async(org_id: str, task: Task, issue_comment: IssueComment):
    new_comment = TaskComment(
        id=issue_comment.id,
        author=issue_comment.user.login,
        body=issue_comment.body,
        created_at=issue_comment.created_at,
    )
    updated_comments = task.comments + [new_comment]
    updated_comments = [comment.model_dump() for comment in updated_comments]
    await get_firestore_client().update_task_async(org_id, task.id, comments=updated_comments)


async def _handle_issue_comment_edited_async(org_id: str, task: Task, issue_comment: IssueComment):
    for i, comment in enumerate(task.comments):
        if comment.id == issue_comment.id:
            comment.body = issue_comment.body
            task.comments[i] = comment
            break
    updated_comments = [comment.model_dump() for comment in task.comments]
    await get_firestore_client().update_task_async(org_id, task.id, comments=updated_comments)


async def _handle_issue_comment_deleted_async(org_id: str, task: Task, issue_comment: IssueComment):
    updated_comments = [comment for comment in task.comments if comment.id != issue_comment.id]
    updated_comments = [comment.model_dump() for comment in updated_comments]
    await get_firestore_client().update_task_async(org_id, task.id, comments=updated_comments)
