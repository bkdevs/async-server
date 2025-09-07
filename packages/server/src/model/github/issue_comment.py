from datetime import datetime

from pydantic import BaseModel

from src.model.github.account import Account


class IssueComment(BaseModel):
    id: int
    body: str
    user: Account
    created_at: datetime
    updated_at: datetime
