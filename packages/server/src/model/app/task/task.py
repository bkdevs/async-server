from datetime import datetime, timezone
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field

from src.model import generate_id
from src.model.app.task.diff import DiffFile


class TaskSource(str, Enum):
    """
    Where the task was ingested from, in app, or GitHub / Linear
    """

    ASYNC = "async"
    GITHUB = "github"
    LINEAR = "linear"


class TaskComment(BaseModel):
    """
    Comments from the ingested TaskSource, e.g., Linear / GitHub comments
    """

    id: int
    author: str
    body: str
    created_at: datetime


class TaskStatus(str, Enum):
    CREATED = "created"
    EXECUTING = "executing"
    PENDING_REVIEW = "pendingReview"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskQuestion(BaseModel):
    question: str
    options: list[str]
    requirements: list[str]


class Task(BaseModel):
    # id fields
    id: str = Field(default_factory=generate_id)
    project_id: str

    # information fields (from ingestion)
    title: str
    body: str
    author: str
    comments: list[TaskComment] = []
    source: TaskSource = TaskSource.ASYNC
    status: TaskStatus = TaskStatus.CREATED

    # Github fields
    github_issue_id: Optional[int] = None
    github_issue_number: Optional[int] = None

    # derived fields
    overview: str = ""
    requirements: list[str] = []
    questions: list[TaskQuestion] = []
    answers: list[str] = []

    # pull request fields
    base_commit: str = ""
    diff_files: list[DiffFile] = []
    pull_request_url: str = ""
    pull_request_branch: str = ""
    preview_url: str = ""

    # datetime fields
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    def get_requirements(self) -> str:
        if not self.requirements:
            return ""
        formatted_requirements = []
        for i, requirement in enumerate(self.requirements, 1):
            formatted_requirements.append(f"{i}. {requirement.strip()}")
        return "\n".join(formatted_requirements)

    def get_ingested_info(self) -> str:
        sections = [f"Title: {self.title}", f"Body: {self.body}"]
        if self.comments:
            sections.append("Comments:")
            for i, comment in enumerate(self.comments, 1):
                comment_text = f"{i}. {comment.author}: {comment.body}"
                sections.append(comment_text)
        return "\n".join(sections)
