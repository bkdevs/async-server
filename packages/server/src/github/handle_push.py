import logging
import traceback

from src.clients import get_firestore_client
from src.model import compute_repository_doc_id
from src.model.github import PushEvent
from src.utils.filesystem_utils import generate_project_tree_async
from src.utils.setup_utils import setup_repo_async

logger = logging.getLogger(__name__)


async def handle_push_async(event: PushEvent):
    """
    Triggered when a commit is pushed to a Github repository.

    When it is pushed to the repository's default branch (e.g. main), we update project's tree.
    """

    if event.ref != f"refs/heads/{event.repository.default_branch}":
        # ignore push to non default branch
        return

    firestore_client = get_firestore_client()
    repository = await firestore_client.get_repository_async(compute_repository_doc_id(event.repository.full_name))
    if not repository:
        return

    try:
        firestore_client = get_firestore_client()
        org = await firestore_client.get_org_async(repository.org_id)
        project = await firestore_client.get_project_async(repository.org_id, repository.project_id)
        repo_directory = await setup_repo_async(org, project)

        updated_project_tree = await generate_project_tree_async(repo_directory)
        if project.tree == updated_project_tree:
            return
        await firestore_client.update_project_async(repository.org_id, repository.project_id, tree=updated_project_tree)
    except Exception:
        logger.error(f"Failed to handle push for: {repository}")
        traceback.print_exc()
        raise
