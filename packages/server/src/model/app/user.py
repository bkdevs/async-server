from datetime import datetime, timezone
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field

from src.model import generate_id


class UserRole(str, Enum):
    ADMIN = "admin"
    MEMBER = "member"


class User(BaseModel):
    id: str = Field(default_factory=generate_id)
    org_id: str = ""
    name: str
    email: str
    role: UserRole = UserRole.MEMBER
    subscribed_tasks: list[str] = []

    # Github
    github_id: Optional[int] = None
    github_login: Optional[str] = None

    # Payment
    stripe_id: str = ""

    # Date
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
