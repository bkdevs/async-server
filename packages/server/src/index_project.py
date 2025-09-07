import asyncio
import logging
import os
import sys
import traceback

from src.agent import AnalyzerAgentMetadata
from src.clients import get_firestore_client, get_github_client
from src.model.agent import AsyncConfig
from src.model.app.project import Language, Project
from src.utils.bootstrap_utils import bootstrap_application_async, create_bootstrap_config
from src.utils.filesystem_utils import cleanup_directory_async, generate_project_tree_async
from src.utils.setup_utils import setup_ephemeral_repo_async

logger = logging.getLogger(__name__)


async def index_project_async(org_id: str, project_id: str, is_dev: bool):
    task_directory = None
    try:
        firestore_client = get_firestore_client()
        org = await firestore_client.get_org_async(org_id)
        project = await firestore_client.get_project_async(org_id, project_id)
        task_directory, repo_directory = await setup_ephemeral_repo_async(org.github_installation_id, project.repo)

        # these operations are fast
        project.tree = await generate_project_tree_async(repo_directory)
        project.languages = await _generate_primary_languages_async(org.github_installation_id, project.repo)
        await firestore_client.update_project_async(org_id, project_id, tree=project.tree, languages=project.languages)

        # extremely slow
        project.overview = await _generate_project_overview_async(project, repo_directory)
        await firestore_client.update_project_async(org_id, project_id, overview=project.overview)

        logger.info(f"Finished indexing project: {project_id}")
    except Exception:
        traceback.print_exc()
        sys.exit(1)
    finally:
        await cleanup_directory_async(task_directory)


async def _generate_project_overview_async(project: Project, repo_directory: str) -> str:
    config = AsyncConfig(
        thread_id=project.id,
        repo_directory=repo_directory,
        project=project,
    )
    agent_metadata = AnalyzerAgentMetadata(config)
    agent = agent_metadata.create_agent()
    response = await agent.ainvoke(
        input={"messages": agent_metadata.get_input_message()},
        config={"configurable": config, "recursion_limit": 500},
    )
    if not response["messages"] or not response["messages"][-1].content:
        raise ValueError("Analzyer agent failed to generate overview")
    return response["messages"][-1].content


async def _generate_primary_languages_async(installation_id: int, repo_full_name: str) -> list[Language]:
    github_client = get_github_client()
    access_token = await github_client.generate_app_access_token_async(installation_id)
    languages = await github_client.get_repository_languages_async(access_token, repo_full_name)
    return _get_primary_languages(languages)


def _get_primary_languages(languages: dict[str, int], threshold: float = 0.05) -> list[Language]:
    total_bytes = sum(languages.values())
    min_bytes = total_bytes * threshold
    primary_languages = []
    for language_str, bytes_used in languages.items():
        language = Language.from_string(language_str)
        if not language or bytes_used < min_bytes:
            continue
        primary_languages.append(language)
    return primary_languages


async def main(org_id: str, project_id: str, is_dev: bool):
    await bootstrap_application_async(create_bootstrap_config(is_dev))

    logger.info("Starting index_project job with params:")
    logger.info(f"  org_id={org_id}")
    logger.info(f"  project_id={project_id}")
    logger.info(f"  is_dev={is_dev}")

    await index_project_async(org_id, project_id, is_dev)


if __name__ == "__main__":
    asyncio.run(
        main(
            org_id=os.getenv("ORG_ID"),
            project_id=os.getenv("PROJECT_ID"),
            is_dev=True,
        )
    )
