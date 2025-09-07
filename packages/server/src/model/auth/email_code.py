from datetime import datetime

from pydantic import BaseModel, Field

from src.model import generate_code, generate_id
from src.model.auth.status import AuthStatus


class EmailCode(BaseModel):
    id: str = Field(default_factory=generate_id)
    code: str = Field(default_factory=generate_code)
    email: str
    user_id: str
    status: AuthStatus
    created_at: datetime
    expires_at: datetime
