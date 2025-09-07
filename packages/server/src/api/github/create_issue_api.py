from pydantic import BaseModel


class CreateIssueRequest(BaseModel):
    user_id: str
    org_id: str
    task_id: str
    is_dev: bool = False


class CreateIssueResponse(BaseModel):
    pass
