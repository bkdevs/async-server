from datetime import datetime, timezone

from pydantic import BaseModel, Field

from src.model import generate_code
from src.model.auth.status import AuthStatus


class Invite(BaseModel):
    id: str
    email: str
    org_id: str
    org_name: str
    from_user_name: str
    status: AuthStatus
    code: str = Field(default_factory=generate_code)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
