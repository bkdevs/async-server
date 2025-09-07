import re

from pydantic import BaseModel

from src.model import compute_pull_request_doc_id


class PullRequest(BaseModel):
    org_id: str
    project_id: str
    task_id: str
    pull_request_url: str

    @property
    def id(self) -> str:
        """
        Firestore ID property that isn't included in serialization
        """
        return compute_pull_request_doc_id(self.pull_request_url)

    @property
    def repo(self) -> str:
        pattern = r"https://github\.com/([^/]+)/([^/]+)/pull/(\d+)"
        match = re.search(pattern, self.pull_request_url)
        if not match:
            raise ValueError(f"Invalid pull request URL: {self.pull_request_url}")

        owner = match.group(1)
        repo = match.group(2)
        return f"{owner}/{repo}"
