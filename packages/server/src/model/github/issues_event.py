from enum import Enum

from pydantic import BaseModel

from src.model.github.account import Account
from src.model.github.issue import Issue
from src.model.github.repository import Repository


class IssuesEventAction(str, Enum):
    ASSIGNED = "assigned"
    CLOSED = "closed"
    DELETED = "deleted"
    DEMILESTONED = "demilestoned"
    EDITED = "edited"
    LABELED = "labeled"
    LOCKED = "locked"
    MILESTONED = "milestoned"
    OPENED = "opened"
    PINNED = "pinned"
    REOPENED = "reopened"
    TRANSFERRED = "transferred"
    TYPED = "typed"
    UNASSIGNED = "unassigned"
    UNLABELED = "unlabeled"
    UNLOCKED = "unlocked"
    UNPINNED = "unpinned"
    UNTYPED = "untyped"


class IssuesEvent(BaseModel):
    action: IssuesEventAction
    issue: Issue
    sender: Account
    repository: Repository
