from enum import Enum

from pydantic import BaseModel

from src.model.app.task import DiffComment


class ReviewAction(str, Enum):
    APPROVE = "approve"
    REQUEST_CHANGES = "request_changes"


class SubmitReviewRequest(BaseModel):
    user_id: str
    org_id: str
    task_id: str
    action: ReviewAction
    comments: list[DiffComment]
    is_dev: bool = False


class SubmitReviewResponse(BaseModel):
    pass
