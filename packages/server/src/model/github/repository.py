from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class Owner(BaseModel):
    login: str
    type: str


class Repository(BaseModel):
    id: int
    name: str
    full_name: str
    default_branch: str
    description: Optional[str]
    owner: Owner
    updated_at: datetime
