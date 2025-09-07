from datetime import datetime, timezone
from typing import Optional

from pydantic import BaseModel, Field

from src.model import generate_id


class MessageEvent(BaseModel):
    id: str = Field(default_factory=generate_id)
    type: str
    in_progress_title: Optional[str] = None
    completed_title: Optional[str] = None
    text: str = ""
    preview: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
