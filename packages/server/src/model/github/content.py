from pydantic import BaseModel


class Content(BaseModel):
    type: str
    encoding: str
    content: str
