from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field

from src.model import generate_id


class MessageStatus(str, Enum):
    IN_PROGRESS = "inProgress"
    COMPLETED = "completed"
    FAILED = "failed"


class MessageAction(BaseModel):
    label: str = Field(
        description=(
            "The type of option to present to the user, e.g., Option 1, Option 2, Option 3"
            "The options should be concise, 40 characters maximum"
        )
    )
    url: Optional[str] = Field(
        default=None,
        description="URL destination to redirect when action is pressed",
    )


class Message(BaseModel):
    id: str = Field(default_factory=generate_id)
    author: str
    title: Optional[str] = None
    text: str = ""
    is_streaming: bool = False
    metadata: dict[str, Any] = {}
    actions: list[MessageAction] = []
    status: MessageStatus = MessageStatus.COMPLETED
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
