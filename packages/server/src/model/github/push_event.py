from pydantic import BaseModel

from src.model.github.account import Account
from src.model.github.repository import Repository


class PushEvent(BaseModel):
    ref: str
    before: str
    after: str
    sender: Account
    repository: Repository
