from pydantic import BaseModel


class Account(BaseModel):
    id: int
    login: str
    type: str
    avatar_url: str
