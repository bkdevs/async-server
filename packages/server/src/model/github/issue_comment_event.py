from enum import Enum

from pydantic import BaseModel

from src.model.github.issue import Issue
from src.model.github.issue_comment import IssueComment
from src.model.github.repository import Repository


class IssueCommentEventAction(str, Enum):
    CREATED = "created"
    EDITED = "edited"
    DELETED = "deleted"


class IssueCommentEvent(BaseModel):
    action: IssueCommentEventAction
    issue: Issue
    comment: IssueComment
    repository: Repository
