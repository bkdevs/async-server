from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from src.model.github.account import Account


class Issue(BaseModel):
    id: int
    number: int
    title: str
    body: Optional[str]
    user: Account
    assignee: Optional[Account]
    created_at: datetime
