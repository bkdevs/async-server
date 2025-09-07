from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel


class DiffCommentSide(str, Enum):
    LEFT = "LEFT"
    RIGHT = "RIGHT"


class DiffComment(BaseModel):
    file_path: str
    body: str
    side: DiffCommentSide
    start_line: int
    end_line: int
    commit_id: Optional[str] = None
    created_at: datetime

    def __str__(self) -> str:
        line_range = f"{self.start_line}-{self.end_line}" if self.start_line != self.end_line else str(self.start_line)
        return f"On {self.file_path} (line {line_range}, {self.side.value} side)\n{self.body}"


class DiffFile(BaseModel):
    file_path: str
    body: str
