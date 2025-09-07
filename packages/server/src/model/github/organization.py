from pydantic import BaseModel


class Organization(BaseModel):
    id: int
    login: str
    description: str
