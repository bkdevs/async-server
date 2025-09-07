import asyncio
import logging
import os
import sys
import traceback
from datetime import datetime, timezone

import aiofiles
from claude_code_sdk import ProcessError
from tenacity import retry, retry_if_exception_type, stop_after_attempt

from src.agent import ClaudeCodeAgent, OutputFormatter
from src.clients import get_firestore_client, get_github_client
from src.model.agent.response import GeneratedSubtasks
from src.model.app import Org
from src.model.app.project import Project
from src.model.app.task import PullRequest, Subtask, SubtaskStatus, Task, TaskStatus
from src.prompt.execute_task_prompt import EXECUTE_TASK_PROMPT, EXECUTE_TASK_SYSTEM_PROMPT
from src.prompt.generate_subtasks_prompt import GENERATE_SUBTASKS_PROMPT
from src.utils.bootstrap_utils import bootstrap_application_async, create_bootstrap_config
from src.utils.diff_utils import generate_diff_files_async
from src.utils.filesystem_utils import cleanup_directory_async
from src.utils.git_utils import (
    add_and_commit_changes,
    create_and_checkout_branch,
    generate_branch_name,
    get_current_commit,
    get_parent_commit,
)
from src.utils.setup_utils import setup_ephemeral_repo_async

logger = logging.getLogger(__name__)


async def execute_task_async(org_id: str, task_id: str, is_dev: bool):
    task_directory = None
    try:
        firestore_client = get_firestore_client()
        await firestore_client.update_task_async(
            org_id, task_id, status=TaskStatus.EXECUTING, updated_at=datetime.now(timezone.utc)
        )

        # clone repo
        org = await firestore_client.get_org_async(org_id)
        task = await firestore_client.get_task_async(org_id, task_id)
        project = await firestore_client.get_project_async(org_id, task.project_id)
        task_directory, repo_directory = await setup_ephemeral_repo_async(org.github_installation_id, project.repo)
        await _generate_claude_md_async(repo_directory, is_dev)

        # record base commit
        base_commit = get_current_commit(repo_directory)
        await firestore_client.update_task_async(org_id, task_id, base_commit=base_commit)

        # generate tasks
        await _generate_subtasks_async(org_id, task, repo_directory, is_dev)

        # execute the tasks
        branch_name = generate_branch_name(task.title)
        create_and_checkout_branch(repo_directory, branch_name)
        subtasks = await _execute_subtasks_async(org, project, task, branch_name, repo_directory, is_dev)

        # raise a PR
        pull_request = await _raise_pull_request_async(org, project, task, subtasks, branch_name)
        await firestore_client.create_pull_request_async(pull_request)

        latest_commit = get_current_commit(repo_directory)
        diff_files = await generate_diff_files_async(repo_directory, latest_commit, base_commit)
        await get_firestore_client().update_task_async(
            org_id,
            task.id,
            diff_files=[diff_file.model_dump() for diff_file in diff_files],
            pull_request_url=pull_request.pull_request_url,
            pull_request_branch=branch_name,
            status=TaskStatus.PENDING_REVIEW,
            updated_at=datetime.now(timezone.utc),
        )

        logger.info(f"Finished executing task: {task_id}")
    except Exception:
        traceback.print_exc()
        await firestore_client.update_task_async(
            org_id, task_id, status=TaskStatus.FAILED, updated_at=datetime.now(timezone.utc)
        )
        sys.exit(1)
    finally:
        await cleanup_directory_async(task_directory)


async def _generate_claude_md_async(repo_directory: str, is_dev: bool):
    try:
        agent = ClaudeCodeAgent(repo_directory, verbose=is_dev)
        await agent.create_claude_md_async()
    except Exception as e:
        logger.error(f"Failed to generate CLAUDE.md: {e}")
        raise


@retry(reraise=True, stop=stop_after_attempt(3), retry=retry_if_exception_type((ProcessError, FileNotFoundError)))
async def _generate_subtasks_async(org_id: str, task: Task, repo_directory: str, is_dev: bool):
    try:
        agent = ClaudeCodeAgent(
            repo_directory,
            model="claude-opus-4-1-20250805",
            permission_mode="plan",
            verbose=is_dev,
        )
        user_prompt = _get_generate_subtasks_user_prompt(task)
        await agent.run_async(user_prompt)
        async with aiofiles.open(f"{repo_directory}/ASYNC_PLAN_BREAKDOWN.json", mode="r", encoding="utf-8") as file:
            formatter = OutputFormatter()
            output = await file.read()
            result = await formatter.format_output_async(output, GeneratedSubtasks)

        firestore_client = get_firestore_client()
        for generated_subtask in result.subtasks:
            subtask = Subtask(
                title=generated_subtask.title,
                steps=generated_subtask.steps,
            )
            await firestore_client.create_subtask_async(org_id, task.id, subtask)
    except Exception as e:
        logger.error(f"Failed to generate tasks: {e}")
        raise


def _get_generate_subtasks_user_prompt(task: Task) -> str:
    prompt_components = [GENERATE_SUBTASKS_PROMPT]
    prompt_components.append(f"- Description: {task.body}")
    prompt_components.append(f"- Requirements: {task.get_requirements()}")
    return "\n".join(prompt_components)


async def _execute_subtasks_async(
    org: Org, project: Project, task: Task, branch_name: str, repo_directory: str, is_dev: bool
) -> list[Subtask]:
    completed_commits = []
    firestore_client = get_firestore_client()
    agent = ClaudeCodeAgent(repo_directory, append_system_prompt=EXECUTE_TASK_SYSTEM_PROMPT, verbose=is_dev)
    subtasks = await firestore_client.get_subtasks_async(org.id, task.id)
    for i, subtask in enumerate(subtasks):
        try:
            await firestore_client.update_subtask_async(
                org_id=org.id,
                task_id=task.id,
                subtask_id=subtask.id,
                status=SubtaskStatus.IN_PROGRESS,
                updated_at=datetime.now(timezone.utc),
            )
            await agent.run_async(prompt=_get_execute_task_prompt(task, subtask, i + 1, completed_commits))

            commit_hash = add_and_commit_changes(repo_directory, subtask.title)
            if commit_hash:
                completed_commits.append(commit_hash)
                await _push_changes_async(org.github_installation_id, project.repo, repo_directory, branch_name)
            await _complete_subtask_async(org.id, task, subtask, repo_directory, commit_hash)

            logger.info(f"Finished executing subtask: {subtask.id}")
        except Exception as e:
            logger.error(f"Failed to execute subtask {subtask.id}: {e}")
            await firestore_client.update_subtask_async(
                org_id=org.id,
                task_id=task.id,
                subtask_id=subtask.id,
                status=SubtaskStatus.FAILED,
                updated_at=datetime.now(timezone.utc),
            )
            raise

    return await firestore_client.get_subtasks_async(org.id, task.id)


async def _complete_subtask_async(
    org_id: str, task: Task, subtask: Subtask, repo_directory: str, commit_hash: str | None
):
    diff_files = []
    if commit_hash:
        base_commit = get_parent_commit(repo_directory, commit_hash)
        diff_files = await generate_diff_files_async(repo_directory, commit_hash, base_commit)

    await get_firestore_client().update_subtask_async(
        org_id=org_id,
        task_id=task.id,
        subtask_id=subtask.id,
        pull_request_commit=commit_hash or "",
        diff_files=[diff_file.model_dump() for diff_file in diff_files],
        status=SubtaskStatus.COMPLETED,
        updated_at=datetime.now(timezone.utc),
    )


def _get_execute_task_prompt(task: Task, subtask: Subtask, subtask_number: int, completed_commits: list[str]) -> str:
    completed_subtask_commits = "\n".join(
        [f"- Subtask {j + 1}: {commit}" for j, commit in enumerate(completed_commits)]
    )
    if not completed_subtask_commits:
        completed_subtask_commits = "No subtasks have been implemented yet."
    return EXECUTE_TASK_PROMPT.format(
        task_title=task.title,
        task_body=task.body,
        task_requirements=task.get_requirements(),
        subtask_number=subtask_number,
        completed_subtask_commits=completed_subtask_commits,
        subtask_title=subtask.title,
        subtask_description=subtask.get_description(),
    )


async def _push_changes_async(installation_id: int, repo_full_name: str, repo_directory: str, branch_name: str):
    github_client = get_github_client()
    access_token = await github_client.generate_app_access_token_async(installation_id)
    await github_client.push_async(access_token, repo_full_name, repo_directory, branch_name)


async def _raise_pull_request_async(
    org: Org,
    project: Project,
    task: Task,
    subtasks: list[Subtask],
    branch_name: str,
) -> PullRequest:
    github_client = get_github_client()
    access_token = await github_client.generate_app_access_token_async(org.github_installation_id)

    pr_body = (
        f"{task.body}\n\n"
        f"## Requirements\n{task.get_requirements()}\n\n"
        f"## Implemented Tasks\n{'\n'.join([f'- {subtask.title}' for subtask in subtasks])}\n\n"
        f"Fixes #{task.github_issue_number}\n\n"
        "Generated with [Async](https://www.async.build)"
    )
    pull_request = await github_client.create_pull_request_async(
        access_token, project.repo, task.title, pr_body, branch_name, project.default_branch
    )

    return PullRequest(
        org_id=org.id,
        project_id=project.id,
        task_id=task.id,
        pull_request_url=pull_request.html_url,
    )


async def main(org_id: str, task_id: str, is_dev: bool):
    await bootstrap_application_async(create_bootstrap_config(is_dev))

    logger.info("Starting execute_task job with params:")
    logger.info(f"  org_id={org_id}")
    logger.info(f"  task_id={task_id}")
    logger.info(f"  is_dev={is_dev}")

    await execute_task_async(org_id, task_id, is_dev)


if __name__ == "__main__":
    asyncio.run(
        main(
            org_id=os.getenv("ORG_ID"),
            task_id=os.getenv("TASK_ID"),
            is_dev=True,
        )
    )
