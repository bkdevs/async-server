import logging
import traceback
from datetime import datetime, timezone

from src.clients import get_firestore_client, get_github_client
from src.github.github_constants import ASYNC_GITHUB_APP_ID, ASYNC_GITHUB_APP_LOGIN
from src.model import compute_pull_request_doc_id
from src.model.app.task import PullRequest, Subtask, SubtaskStatus, TaskStatus
from src.model.github import PullRequestEvent, PullRequestEventAction
from src.utils.diff_utils import generate_diff_files_async
from src.utils.filesystem_utils import cleanup_directory_async
from src.utils.git_utils import checkout_branch, get_commit_message, get_parent_commit
from src.utils.setup_utils import setup_ephemeral_repo_async

logger = logging.getLogger(__name__)


async def handle_pull_request_async(event: PullRequestEvent):
    if event.sender.id == ASYNC_GITHUB_APP_ID and event.sender.login == ASYNC_GITHUB_APP_LOGIN:
        # updated by Async, already handled in execute_task or revise_task
        return

    firestore_client = get_firestore_client()
    pull_request_id = compute_pull_request_doc_id(event.pull_request.html_url)
    pull_request = await firestore_client.get_pull_request_async(pull_request_id)
    if not pull_request:
        # pull request not opened by Async
        return

    match event.action:
        case PullRequestEventAction.SYNCHRONIZE:
            await _handle_synchronize_async(pull_request, event.pull_request.head.sha)
        case PullRequestEventAction.CLOSED:
            await _handle_closed_async(
                org_id=pull_request.org_id,
                task_id=pull_request.task_id,
                repo_full_name=event.repository.full_name,
                branch_name=event.pull_request.head.ref,
                installation_id=event.installation.id,
                merged=event.pull_request.merged,
            )
        case _:
            pass


async def _handle_synchronize_async(pull_request: PullRequest, commit_hash: str):
    task_directory = None
    try:
        firestore_client = get_firestore_client()
        org = await firestore_client.get_org_async(pull_request.org_id)
        project = await firestore_client.get_project_async(pull_request.org_id, pull_request.project_id)
        task_directory, repo_directory = await setup_ephemeral_repo_async(org.github_installation_id, project.repo)

        commit_message = get_commit_message(repo_directory, commit_hash)
        if commit_message == "Address user feedback":
            # HACK: this is to not double create subtask when revise ran locally
            return

        task = await firestore_client.get_task_async(pull_request.org_id, pull_request.task_id)
        checkout_branch(repo_directory, task.pull_request_branch)

        base_commit = get_parent_commit(repo_directory, commit_hash)
        diff_files = await generate_diff_files_async(repo_directory, commit_hash, base_commit)
        subtask = Subtask(
            title=commit_message,
            steps=[],
            diff_files=diff_files,
            pull_request_commit=commit_hash,
            status=SubtaskStatus.COMPLETED,
        )
        await firestore_client.create_subtask_async(pull_request.org_id, pull_request.task_id, subtask)

        diff_files = await generate_diff_files_async(repo_directory, commit_hash, task.base_commit)
        await firestore_client.update_task_async(
            org_id=pull_request.org_id,
            task_id=pull_request.task_id,
            diff_files=[diff_file.model_dump() for diff_file in diff_files],
            updated_at=datetime.now(timezone.utc),
        )
    except Exception:
        logger.error(f"Failed to handle pull_request::synchronize for: {pull_request}")
        traceback.print_exc()
        raise
    finally:
        await cleanup_directory_async(task_directory)


async def _handle_closed_async(
    org_id: str, task_id: str, repo_full_name: str, branch_name: str, installation_id: int, merged: bool
):
    status = TaskStatus.COMPLETED if merged else TaskStatus.CANCELLED
    await get_firestore_client().update_task_async(
        org_id, task_id, status=status, updated_at=datetime.now(timezone.utc)
    )

    github_client = get_github_client()
    access_token = await github_client.generate_app_access_token_async(installation_id)
    await github_client.delete_branch_async(access_token, repo_full_name, branch_name)
