import asyncio
import base64
import re
import time
from typing import AsyncGenerator, Optional

import httpx
import jwt
from async_lru import alru_cache

from src.model.github import (
    Content,
    Installation,
    Issue,
    IssueComment,
    PullRequest,
    PullRequestComment,
    PullRequestFile,
    Repository,
)


class GithubClient:
    """
    Async wrapper class for GitHub API
    """

    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0)

    async def close_async(self):
        """
        Close the httpx client
        """
        await self.client.aclose()

    # ========================================
    # USER OPERATIONS
    # ========================================

    async def get_access_token_async(self, client_id: str, client_secret: str, github_code: str) -> str:
        headers = {"Accept": "application/json"}
        data = {
            "client_id": client_id,
            "client_secret": client_secret,
            "code": github_code,
        }
        response = await self._post_request_async(
            url="https://github.com/login/oauth/access_token",
            headers=headers,
            data=data,
        )
        return response.json().get("access_token")

    async def get_user_information_async(self, access_token: str) -> tuple[int, str]:
        """
        Get user's Github ID and login
        """
        headers = self._get_base_headers(access_token)
        user_response = await self._get_request_async("https://api.github.com/user", headers)
        user_data = user_response.json()
        return user_data.get("id"), user_data.get("login")

    # ========================================
    # GIT OPERATIONS
    # ========================================

    async def clone_repo_async(self, access_token: str, full_repo_name: str, task_directory: str) -> str:
        repo_url = f"https://git:{access_token}@github.com/{full_repo_name}.git"
        repo_name = full_repo_name.split("/")[1]
        repo_directory = f"{task_directory}/{repo_name}"
        process = await asyncio.create_subprocess_exec(
            "git",
            "clone",
            repo_url,
            repo_directory,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        await process.communicate()
        return repo_directory

    async def push_async(self, access_token: str, full_repo_name: str, repo_directory: str, branch_name: str) -> None:
        repo_url = f"https://git:{access_token}@github.com/{full_repo_name}.git"
        process = await asyncio.create_subprocess_exec(
            "git",
            "push",
            repo_url,
            branch_name,
            cwd=repo_directory,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        _, stderr = await process.communicate()
        if process.returncode != 0:
            raise RuntimeError(f"Git push failed: {stderr.decode()}")

    async def pull_async(
        self, access_token: str, full_repo_name: str, repo_directory: str, branch_name: str = "main"
    ) -> None:
        repo_url = f"https://git:{access_token}@github.com/{full_repo_name}.git"
        process = await asyncio.create_subprocess_exec(
            "git",
            "pull",
            "--no-rebase",
            repo_url,
            branch_name,
            cwd=repo_directory,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        _, stderr = await process.communicate()
        if process.returncode != 0:
            raise RuntimeError(f"Git pull failed: {stderr.decode()}")

    # ========================================
    # GITHUB APP INSTALLATION OPERATIONS
    # ========================================

    async def get_installation_async(self, installation_id: int) -> Installation:
        jwt_token = await self._generate_jwt_token_async()
        headers = {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {jwt_token}",
        }
        response = await self._get_request_async(f"https://api.github.com/app/installations/{installation_id}", headers)
        return Installation(**response.json())

    async def list_installation_repos_async(self, access_token: str) -> AsyncGenerator[Repository, None]:
        headers = self._get_base_headers(access_token)
        url = "https://api.github.com/installation/repositories"
        while url:
            response = await self._get_request_async(url, headers)
            for repo_json in response.json().get("repositories", []):
                yield Repository(**repo_json)
            url = self._get_next_url(response.headers.get("link"))

    # ========================================
    # REPOSITORY OPERATIONS
    # ========================================

    async def get_repository_content_async(
        self, access_token: str, full_repo_name: str, file_path: str, sha: str
    ) -> str:
        response = await self._get_request_async(
            url=f"https://api.github.com/repos/{full_repo_name}/contents/{file_path}?ref={sha}",
            headers=self._get_base_headers(access_token),
        )
        content = Content(**response.json())
        return base64.b64decode(content.content).decode("utf-8")

    async def delete_branch_async(self, access_token: str, repo_full_name: str, branch_name: str) -> None:
        url = f"https://api.github.com/repos/{repo_full_name}/git/refs/heads/{branch_name}"
        response = await self._delete_request_async(url, self._get_base_headers(access_token))
        response.raise_for_status()

    async def get_repository_languages_async(self, access_token: str, repo_full_name: str) -> dict[str, int]:
        url = f"https://api.github.com/repos/{repo_full_name}/languages"
        response = await self._get_request_async(url, self._get_base_headers(access_token))
        return response.json()

    # ========================================
    # REPOSITORY ISSUE OPERATIONS
    # ========================================

    async def list_repository_open_issues_async(
        self, access_token: str, repo_full_name: str
    ) -> AsyncGenerator[Issue, None]:
        headers = self._get_base_headers(access_token)
        url = f"https://api.github.com/repos/{repo_full_name}/issues?state=open"
        while url:
            response = await self._get_request_async(url, headers)
            for issue_json in response.json():
                if issue_json.get("pull_request"):
                    continue
                yield Issue(**issue_json)
            url = self._get_next_url(response.headers.get("link"))

    async def list_issue_comments_async(
        self, access_token: str, repo_full_name: str, issue_number: int
    ) -> AsyncGenerator[IssueComment, None]:
        headers = self._get_base_headers(access_token)
        url = f"https://api.github.com/repos/{repo_full_name}/issues/{issue_number}/comments"
        while url:
            response = await self._get_request_async(url, headers)
            for issue_comment_json in response.json():
                yield IssueComment(**issue_comment_json)
            url = self._get_next_url(response.headers.get("link"))

    async def create_issue_async(
        self,
        access_token: str,
        repo_full_name: str,
        title: str,
        body: str,
        assignee: str,
    ) -> Issue:
        headers = self._get_base_headers(access_token)
        url = f"https://api.github.com/repos/{repo_full_name}/issues"
        data = {
            "title": title,
            "body": body,
            "assignee": assignee,
        }
        response = await self._post_request_json_async(url, headers, data)
        return Issue(**response.json())

    async def create_issue_comment_async(
        self,
        access_token: str,
        repo_full_name: str,
        issue_number: int,
        body: str,
    ) -> IssueComment:
        headers = self._get_base_headers(access_token)
        url = f"https://api.github.com/repos/{repo_full_name}/issues/{issue_number}/comments"
        data = {
            "body": body,
        }
        response = await self._post_request_json_async(url, headers, data)
        return IssueComment(**response.json())

    async def update_issue_async(
        self,
        access_token: str,
        repo_full_name: str,
        issue_number: int,
        state: str = None,
        state_reason: str = None,
        body: str = None,
    ) -> Issue:
        headers = self._get_base_headers(access_token)
        url = f"https://api.github.com/repos/{repo_full_name}/issues/{issue_number}"
        data = {}
        if state:
            data["state"] = state
        if state_reason:
            data["state_reason"] = state_reason
        if body is not None:
            data["body"] = body
        response = await self._patch_request_json_async(url, headers, data)
        return Issue(**response.json())

    # ========================================
    # PULL REQUEST OPERATIONS
    # ========================================

    async def create_pull_request_async(
        self, access_token: str, repo_full_name: str, title: str, body: str, head: str, base: str = "main"
    ) -> PullRequest:
        headers = self._get_base_headers(access_token)
        url = f"https://api.github.com/repos/{repo_full_name}/pulls"
        data = {
            "title": title,
            "body": body,
            "head": head,
            "base": base,
        }
        response = await self._post_request_json_async(url, headers, data)
        return PullRequest(**response.json())

    async def get_pull_request_async(
        self, access_token: str, repo_full_name: str, pull_request_number: int
    ) -> PullRequest:
        response = await self._get_request_async(
            url=f"https://api.github.com/repos/{repo_full_name}/pulls/{pull_request_number}",
            headers=self._get_base_headers(access_token),
        )
        return PullRequest(**response.json())

    async def list_pull_request_files_async(
        self, access_token: str, repo_full_name: str, pull_request_number: int
    ) -> AsyncGenerator[PullRequestFile, None]:
        headers = self._get_base_headers(access_token)
        url = f"https://api.github.com/repos/{repo_full_name}/pulls/{pull_request_number}/files"
        while url:
            response = await self._get_request_async(url, headers)
            for pull_request_file_json in response.json():
                yield PullRequestFile(**pull_request_file_json)
            url = self._get_next_url(response.headers.get("link"))

    async def list_pull_request_comments_async(
        self, access_token: str, repo_full_name: str, pull_request_number: int
    ) -> AsyncGenerator[PullRequestComment, None]:
        headers = self._get_base_headers(access_token)
        url = f"https://api.github.com/repos/{repo_full_name}/pulls/{pull_request_number}/comments"
        while url:
            response = await self._get_request_async(url, headers)
            for pull_request_comment_json in response.json():
                yield PullRequestComment(**pull_request_comment_json)
            url = self._get_next_url(response.headers.get("link"))

    async def create_pull_request_review_async(
        self,
        access_token: str,
        repo_full_name: str,
        pull_request_number: int,
        body: str,
        event: str,
        comments: list = None,
    ) -> dict[str, any]:
        headers = self._get_base_headers(access_token)
        url = f"https://api.github.com/repos/{repo_full_name}/pulls/{pull_request_number}/reviews"
        data = {
            "body": body,
            "event": event,
        }
        if comments:
            data["comments"] = comments
        response = await self._post_request_json_async(url, headers, data)
        return response.json()

    async def create_pull_request_review_comment_async(
        self, access_token: str, repo_full_name: str, pull_request_number: int, comment_data: dict
    ) -> dict[str, any]:
        headers = self._get_base_headers(access_token)
        url = f"https://api.github.com/repos/{repo_full_name}/pulls/{pull_request_number}/comments"
        response = await self._post_request_json_async(url, headers, comment_data)
        return response.json()

    async def merge_pull_request_async(
        self,
        access_token: str,
        repo_full_name: str,
        pull_request_number: int,
        commit_title: str,
        merge_method: str = "squash",
    ) -> dict[str, any]:
        headers = self._get_base_headers(access_token)
        url = f"https://api.github.com/repos/{repo_full_name}/pulls/{pull_request_number}/merge"
        data = {
            "commit_title": commit_title,
            "merge_method": merge_method,
        }
        response = await self._put_request_json_async(url, headers, data)
        return response.json()

    # ========================================
    # APP TOKEN
    # ========================================

    @alru_cache(ttl=3000)
    async def generate_app_access_token_async(self, installation_id: int) -> str:
        jwt_token = await self._generate_jwt_token_async()
        headers = {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {jwt_token}",
        }
        response = await self._post_request_async(
            f"https://api.github.com/app/installations/{installation_id}/access_tokens", headers
        )
        return response.json().get("token")

    # ========================================
    # PRIVATE METHODS
    # ========================================

    async def _get_request_async(self, url: str, headers: dict[str, str]) -> httpx.Response:
        response = await self.client.get(url, headers=headers)
        response.raise_for_status()
        return response

    async def _post_request_async(self, url: str, headers: dict[str, str], data: dict[str, str] = {}) -> httpx.Response:
        response = await self.client.post(url, headers=headers, data=data)
        response.raise_for_status()
        return response

    async def _delete_request_async(self, url: str, headers: dict[str, str]) -> httpx.Response:
        response = await self.client.delete(url, headers=headers)
        response.raise_for_status()
        return response

    async def _post_request_json_async(
        self, url: str, headers: dict[str, str], data: dict[str, str] = {}
    ) -> httpx.Response:
        response = await self.client.post(url, headers=headers, json=data)
        response.raise_for_status()
        return response

    async def _put_request_json_async(
        self, url: str, headers: dict[str, str], data: dict[str, str] = {}
    ) -> httpx.Response:
        response = await self.client.put(url, headers=headers, json=data)
        response.raise_for_status()
        return response

    async def _patch_request_json_async(
        self, url: str, headers: dict[str, str], data: dict[str, str] = {}
    ) -> httpx.Response:
        response = await self.client.patch(url, headers=headers, json=data)
        response.raise_for_status()
        return response

    async def _generate_jwt_token_async(self):
        from src.clients import get_secret_client

        secret_client = get_secret_client()
        client_id = await secret_client.get_async_github_app_client_id_async()
        private_key = await secret_client.get_async_github_app_private_key_async()
        payload = {
            "iat": int(time.time()),
            "exp": int(time.time() + 600),
            "iss": client_id,
        }
        return jwt.encode(payload, private_key, algorithm="RS256")

    def _get_base_headers(self, access_token: str) -> dict[str, str]:
        return {
            "Accept": "application/vnd.github+json",
            "Authorization": f"token {access_token}",
        }

    def _get_next_url(self, raw_link: Optional[str]) -> Optional[str]:
        if not raw_link:
            return None

        links = {}
        for link in raw_link.split(","):
            link = link.strip()
            url_match = re.search(r"<([^>]+)>", link)
            rel_match = re.search(r'rel="([^"]+)"', link)
            if url_match and rel_match:
                url = url_match.group(1)
                rel = rel_match.group(1)
                links[rel] = url
        return links.get("next")
