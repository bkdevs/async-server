import re
import uuid
from urllib.parse import urlparse

from git import Repo

BRANCH_NAME_PREFIX = "async"

# file names that should not be commited
EXCLUDED_FILES = ["CLAUDE.md", "ASYNC_PLAN_BREAKDOWN.json"]


def generate_branch_name(task_title: str, prefix: str = BRANCH_NAME_PREFIX, max_words: int = 4):
    branch_name = task_title.lower().strip()
    branch_name = re.sub(r"[^\w\s-]", "", branch_name)

    words = branch_name.split()[:max_words]
    branch_name = "-".join(words)
    branch_name = re.sub(r"-+", "-", branch_name)
    branch_name = branch_name.strip("-")

    if not branch_name:
        return f"{prefix}/{uuid.uuid4()}"
    return f"{prefix}/{branch_name}-{str(uuid.uuid4())[:8]}"


def create_and_checkout_branch(repo_directory: str, branch_name: str):
    repo = Repo(repo_directory)
    repo.git.checkout("-b", branch_name)


def checkout_branch(repo_directory: str, branch_name: str):
    repo = Repo(repo_directory)
    repo.git.checkout(branch_name)


def add_and_commit_changes(
    repo_directory: str, commit_message: str, excluded_files: list[str] = EXCLUDED_FILES
) -> str | None:
    repo = Repo(repo_directory)
    repo.git.add("-A")

    staged_files = repo.git.diff("--cached", "--name-only").splitlines()
    staged_files_set = set(staged_files)
    if staged_files_set.issubset(set(excluded_files)):
        # sometimes the subtask does not make any changes, usually because the prior subtask already does its work
        return None

    for excluded_file in excluded_files:
        if excluded_file in staged_files:
            repo.git.reset("HEAD", excluded_file)

    repo.git.config("user.name", "Async")
    repo.git.config("user.email", "email@domain")
    repo.git.commit("-m", commit_message)
    return repo.head.commit.hexsha


def get_current_commit(repo_directory: str) -> str:
    repo = Repo(repo_directory)
    return repo.head.commit.hexsha


def get_parent_commit(repo_directory: str, commit_hash: str) -> str | None:
    repo = Repo(repo_directory)
    commit = repo.commit(commit_hash)
    if commit.parents:
        return commit.parents[0].hexsha
    return None


def get_changed_files_from_commit(
    repo_directory: str, head_commit_hash: str, base_commit_hash: str | None = None
) -> list[str]:
    repo = Repo(repo_directory)
    if base_commit_hash:
        changed_files = repo.git.diff("--name-only", base_commit_hash, head_commit_hash).splitlines()
    else:
        changed_files = repo.git.show("--name-only", "--format=", head_commit_hash).splitlines()
    return [f for f in changed_files if f.strip()]


def get_file_content_at_commit(repo_directory: str, file_path: str, commit_hash: str | None) -> str:
    if not commit_hash:
        return ""

    repo = Repo(repo_directory)
    try:
        blob = repo.commit(commit_hash).tree[file_path]
        return blob.data_stream.read().decode("utf-8")
    except KeyError:
        return ""


def get_commit_message(repo_directory: str, commit_hash: str) -> str:
    repo = Repo(repo_directory)
    commit = repo.commit(commit_hash)
    return commit.message.strip()


def parse_pull_request_number(pull_request_url: str) -> int:
    parsed = urlparse(pull_request_url)
    parts = parsed.path.strip("/").split("/")
    if len(parts) >= 4 and parts[2] == "pull":
        return int(parts[3])
    else:
        raise ValueError("URL is not a valid GitHub pull request URL.")
