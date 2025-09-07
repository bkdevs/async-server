from pydantic import BaseModel

from src.model.github import Repository


class OnboardProjectsRequest(BaseModel):
    user_id: str
    org_id: str
    repos: list[Repository]
    is_dev: bool = False


class OnboardProjectsResponse(BaseModel):
    pass
