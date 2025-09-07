import os
import uuid

from src.clients import get_github_client
from src.model.app import Org
from src.model.app.project import Project
from src.utils.filesystem_utils import create_directory_async

BASE_DIRECTORY = "/tmp/async"


async def setup_repo_async(org: Org, project: Project) -> str:
    org_directory = f"{BASE_DIRECTORY}/{org.name}"
    if not os.path.exists(org_directory):
        await create_directory_async(org_directory)

    github_client = get_github_client()
    access_token = await github_client.generate_app_access_token_async(org.github_installation_id)
    repo_directory = f"{org_directory}/{project.name}"
    if os.path.exists(repo_directory):
        await github_client.pull_async(access_token, project.repo, repo_directory)
        return repo_directory

    repo_directory = await github_client.clone_repo_async(access_token, project.repo, org_directory)
    return repo_directory


async def setup_ephemeral_repo_async(installation_id: int, full_repo_name: str) -> tuple[str, str]:
    task_directory = f"{BASE_DIRECTORY}/{uuid.uuid4()}"
    await create_directory_async(task_directory)

    github_client = get_github_client()
    access_token = await github_client.generate_app_access_token_async(installation_id)
    repo_directory = await github_client.clone_repo_async(access_token, full_repo_name, task_directory)
    return task_directory, repo_directory
