from pydantic import BaseModel

from src.model.github import Repository


class OnboardGithubRequest(BaseModel):
    user_id: str
    code: str
    installation_id: int
    is_dev: bool = False


class OnboardGithubResponse(BaseModel):
    repos: list[Repository]
