from datetime import datetime

from pydantic import BaseModel, Field

from src.model import generate_id


class Lead(BaseModel):
    id: str = Field(default_factory=generate_id)
    email: str
    company: str
    role: str
    message: str
    created_at: datetime = Field(default_factory=datetime.now)
