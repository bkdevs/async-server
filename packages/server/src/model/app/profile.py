from pydantic import BaseModel


class Profile(BaseModel):
    id: str
    name: str
    email: str = ""
