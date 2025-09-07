from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, status

from src.api.github import ReviewAction, SubmitReviewRequest, SubmitReviewResponse
from src.clients import get_firestore_client, get_github_client, get_secret_client
from src.model.app.task import DiffComment, Subtask, Task
from src.model.app.task.subtask import SubtaskStatus
from src.utils.git_utils import parse_pull_request_number

router = APIRouter()


@router.post("/submit-review", status_code=status.HTTP_200_OK)
async def submit_review_async(request: SubmitReviewRequest) -> SubmitReviewResponse:
    firestore_client = get_firestore_client()
    task = await firestore_client.get_task_async(request.org_id, request.task_id)
    subtasks = await firestore_client.get_subtasks_async(request.org_id, task.id)
    project = await firestore_client.get_project_async(request.org_id, task.project_id)

    for comment in request.comments:
        if not comment.commit_id:
            comment.commit_id = subtasks[-1].pull_request_commit

    await _update_tasks_with_diff_comments_async(request.org_id, request.task_id, subtasks, request.comments)

    access_token = await get_secret_client().get_user_github_token_async(request.user_id)
    pull_request_number = parse_pull_request_number(task.pull_request_url)
    review_body = _get_review_body(request.action, request.comments)
    await get_github_client().create_pull_request_review_async(
        access_token, project.repo, pull_request_number, review_body, request.action.upper()
    )

    match request.action:
        case ReviewAction.APPROVE:
            await _handle_approve_async(access_token, task, project.repo, pull_request_number)
        case ReviewAction.REQUEST_CHANGES:
            await _handle_request_changes_async(request.org_id, task, subtasks, request.is_dev)
        case _:
            pass

    return SubmitReviewResponse()


def _get_review_body(action: ReviewAction, comments: list[DiffComment]) -> str:
    base_message = "Approved" if action == ReviewAction.APPROVE else "Changes Requested"
    if not comments:
        return base_message

    comment_text = "\n\n".join(str(comment) for comment in comments)
    return f"{base_message}\n\n{comment_text}"


async def _update_tasks_with_diff_comments_async(
    org_id: str, task_id: str, subtasks: list[Subtask], diff_comments: list[DiffComment]
):
    if not diff_comments or not subtasks:
        return

    comments_by_commit = {}
    for comment in diff_comments:
        commit_id = comment.commit_id
        if commit_id not in comments_by_commit:
            comments_by_commit[commit_id] = []
        comments_by_commit[commit_id].append(comment)

    firestore_client = get_firestore_client()
    for subtask in subtasks:
        if not subtask.pull_request_commit or subtask.pull_request_commit not in comments_by_commit:
            continue

        matching_comments = comments_by_commit[subtask.pull_request_commit]
        await firestore_client.update_subtask_async(
            org_id,
            task_id,
            subtask.id,
            diff_comments=[comment.model_dump() for comment in matching_comments],
            updated_at=datetime.now(timezone.utc),
        )
        subtask.diff_comments = matching_comments


async def _handle_approve_async(access_token: str, task: Task, repo_full_name: str, pull_request_number: int):
    github_client = get_github_client()
    response = await github_client.merge_pull_request_async(
        access_token, repo_full_name, pull_request_number, task.title
    )
    if not response.get("merged", False):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to merge pull request {pull_request_number}: {response.get('message')}",
        )


async def _handle_request_changes_async(org_id: str, task: Task, subtasks: list[Subtask], is_dev: bool):
    # TODO: disabling remote revise for now
    # await _create_feedback_subtask_async(org_id, task, subtasks)
    # await get_firestore_client().update_task_async(
    #     org_id=org_id,
    #     task_id=task.id,
    #     status=TaskStatus.EXECUTING,
    #     updated_at=datetime.now(timezone.utc),
    # )
    # await get_async_client().invoke_revise_task_job_async(org_id, task.id, is_dev)
    pass


async def _create_feedback_subtask_async(org_id: str, task: Task, subtasks: list[Subtask]) -> Subtask:
    firestore_client = get_firestore_client()
    comments = []
    for subtask in subtasks:
        if not subtask.diff_comments:
            continue
        for comment in subtask.diff_comments:
            comments.append(comment)

    if not comments:
        raise ValueError("No feedback comments found to address")

    steps = []
    for i, comment in enumerate(comments, 1):
        step = f"Address comment {i}: '{comment.body[:50]}...' in {comment.file_path} (lines {comment.start_line}-{comment.end_line})"
        steps.append(step)

    feedback_subtask = Subtask(
        title="Address user feedback",
        steps=steps,
        status=SubtaskStatus.IN_PROGRESS,
    )
    return await firestore_client.create_subtask_async(org_id, task.id, feedback_subtask)
