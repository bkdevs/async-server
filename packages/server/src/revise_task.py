import asyncio
import logging
import os
import sys
import traceback
from datetime import datetime, timezone

from src.agent import ClaudeCodeAgent
from src.clients import get_firestore_client, get_github_client
from src.model.app import Org
from src.model.app.project import Project
from src.model.app.task import Subtask, SubtaskStatus, Task, TaskStatus
from src.prompt.execute_task_prompt import REMOVE_COMMENTS_PROMPT
from src.prompt.revise_task_prompt import REVISE_TASK_PROMPT
from src.utils.bootstrap_utils import bootstrap_application_async, create_bootstrap_config
from src.utils.diff_utils import generate_diff_files_async
from src.utils.filesystem_utils import cleanup_directory_async
from src.utils.git_utils import add_and_commit_changes, checkout_branch, get_parent_commit
from src.utils.setup_utils import setup_ephemeral_repo_async

logger = logging.getLogger(__name__)


async def revise_task_async(org_id: str, task_id: str, is_dev: bool):
    task_directory = None
    try:
        firestore_client = get_firestore_client()
        org = await firestore_client.get_org_async(org_id)
        task = await firestore_client.get_task_async(org_id, task_id)
        project = await firestore_client.get_project_async(org_id, task.project_id)
        feedback_subtask = await firestore_client.get_latest_subtask_async(org_id, task.id)

        task_directory, repo_directory = await setup_ephemeral_repo_async(org.github_installation_id, project.repo)
        checkout_branch(repo_directory, task.pull_request_branch)

        await firestore_client.update_task_async(
            org_id=org_id,
            task_id=task_id,
            status=TaskStatus.EXECUTING,
            updated_at=datetime.now(timezone.utc),
        )
        await _run_subtask_async(org, project, task, feedback_subtask, repo_directory, is_dev)
        feedback_subtask = await firestore_client.get_subtask_async(org_id, task_id, feedback_subtask.id)

        diff_files = await generate_diff_files_async(
            repo_directory, feedback_subtask.pull_request_commit, task.base_commit
        )
        await firestore_client.update_task_async(
            org_id=org_id,
            task_id=task_id,
            diff_files=[diff_file.model_dump() for diff_file in diff_files],
            status=TaskStatus.PENDING_REVIEW,
            ast_updated=datetime.now(timezone.utc),
        )

        logger.info(f"Finished revising task: {task_id}")
    except Exception:
        traceback.print_exc()
        await firestore_client.update_task_async(
            org_id=org_id,
            task_id=task_id,
            status=TaskStatus.FAILED,
            ast_updated=datetime.now(timezone.utc),
        )
        sys.exit(1)
    finally:
        await cleanup_directory_async(task_directory)


async def _run_subtask_async(
    org: Org, project: Project, task: Task, subtask: Subtask, repo_directory: str, is_dev: bool
):
    firestore_client = get_firestore_client()
    try:
        await firestore_client.update_subtask_async(
            org_id=org.id,
            task_id=task.id,
            subtask_id=subtask.id,
            status=SubtaskStatus.IN_PROGRESS,
            updated_at=datetime.now(timezone.utc),
        )
        agent = ClaudeCodeAgent(repo_directory, verbose=is_dev)
        await agent.run_async(prompt=_get_revise_prompt(task, subtask))
        await agent.run_async(prompt=REMOVE_COMMENTS_PROMPT)

        commit_hash = add_and_commit_changes(repo_directory, "Addressed user feedback")
        await _push_changes_async(org.github_installation_id, project.repo, repo_directory, task.pull_request_branch)

        base_commit = get_parent_commit(repo_directory, commit_hash)
        diff_files = await generate_diff_files_async(repo_directory, commit_hash, base_commit)
        await firestore_client.update_subtask_async(
            org_id=org.id,
            task_id=task.id,
            subtask_id=subtask.id,
            pull_request_commit=commit_hash or "",
            diff_files=[diff_file.model_dump() for diff_file in diff_files],
            status=SubtaskStatus.COMPLETED,
            updated_at=datetime.now(timezone.utc),
        )
    except Exception:
        logger.error(f"Failed to run subtask: {subtask.id}")
        await firestore_client.update_subtask_async(
            org_id=org.id,
            task_id=task.id,
            subtask_id=subtask.id,
            status=SubtaskStatus.FAILED,
            updated_at=datetime.now(timezone.utc),
        )
        raise


def _get_revise_prompt(task: Task, feedback_task: Subtask) -> str:
    return REVISE_TASK_PROMPT.format(
        task_title=task.title,
        task_requirements=task.get_requirements(),
        feedback_task_description=feedback_task.get_description(),
    )


async def _push_changes_async(installation_id: int, repo_full_name: str, repo_directory: str, branch_name: str):
    github_client = get_github_client()
    access_token = await github_client.generate_app_access_token_async(installation_id)
    await github_client.push_async(access_token, repo_full_name, repo_directory, branch_name)


async def main(org_id: str, task_id: str, is_dev: bool):
    await bootstrap_application_async(create_bootstrap_config(is_dev))

    logger.info("Starting revise_task job with params:")
    logger.info(f"  org_id={org_id}")
    logger.info(f"  task_id={task_id}")
    logger.info(f"  is_dev={is_dev}")

    await revise_task_async(org_id, task_id, is_dev)


if __name__ == "__main__":
    asyncio.run(
        main(
            org_id=os.getenv("ORG_ID"),
            task_id=os.getenv("TASK_ID"),
            is_dev=True,
        )
    )
