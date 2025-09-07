from pydantic import BaseModel


class CreateIssueCommentRequest(BaseModel):
    user_id: str
    org_id: str
    task_id: str
    comment_body: str


class CreateIssueCommentResponse(BaseModel):
    comment_id: int
