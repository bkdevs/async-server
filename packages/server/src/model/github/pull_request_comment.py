from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from src.model.github.account import Account


class PullRequestComment(BaseModel):
    id: int
    created_at: datetime
    user: Account
    path: str
    body: str
    side: str
    start_line: Optional[int] = None
    line: int
    original_start_line: Optional[int] = None
    original_line: int
    in_reply_to_id: Optional[int] = None
