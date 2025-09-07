from pydantic import BaseModel


class AuthGithubRequest(BaseModel):
    user_id: str
    code: str
    is_dev: bool = False


class AuthGithubResponse(BaseModel):
    pass
