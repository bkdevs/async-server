from pydantic import BaseModel


class CreatePullRequestRequest(BaseModel):
    org_id: str
    task_id: str
    branch_name: str
    is_dev: bool = False


class CreatePullRequestResponse(BaseModel):
    pass
