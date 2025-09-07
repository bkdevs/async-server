import re
import secrets


def generate_id(length: int = 20) -> str:
    """
    Generates a firestore-esque random ID.

    We do this locally prior to document ID creation to avoid having to wait on the response
    and to have id _always_ present as a field in the model
    """
    chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
    return "".join(secrets.choice(chars) for _ in range(length))


def generate_code(length: int = 6) -> str:
    """
    Generates a random numeric code for an invite
    """
    chars = "0123456789"
    return "".join(secrets.choice(chars) for _ in range(length))


def compute_pull_request_doc_id(pull_request_url: str) -> str:
    pattern = r"https://github\.com/([^/]+)/([^/]+)/pull/(\d+)"
    match = re.search(pattern, pull_request_url)
    if not match:
        raise ValueError(f"Invalid pull request URL: {pull_request_url}")

    owner = match.group(1)
    repo = match.group(2)
    number = match.group(3)
    return f"{owner}::{repo}::{number}"


def compute_repository_doc_id(repo_full_name: str) -> str:
    return repo_full_name.replace("/", "::::")
