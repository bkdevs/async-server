from pydantic import BaseModel

from src.model.github.account import Account


class Installation(BaseModel):
    id: int
    account: Account
