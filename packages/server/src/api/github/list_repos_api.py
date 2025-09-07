from pydantic import BaseModel

from src.model.github import Repository


class ListReposRequest(BaseModel):
    org_id: str
    is_dev: bool = False


class ListReposResponse(BaseModel):
    repos: list[Repository]
