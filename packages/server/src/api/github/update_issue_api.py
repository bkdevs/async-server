from enum import Enum
from typing import Optional

from pydantic import BaseModel


class UpdateIssueAction(Enum):
    CLOSE_AS_COMPLETE = "close_as_complete"
    DELETE = "delete"
    UPDATE_BODY = "update_body"


class UpdateIssueRequest(BaseModel):
    user_id: str
    org_id: str
    task_id: str
    action: UpdateIssueAction
    body: Optional[str] = None
    is_dev: bool = False


class UpdateIssueResponse(BaseModel):
    pass
