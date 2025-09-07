from enum import Enum

from pydantic import BaseModel

from src.model.github.account import Account
from src.model.github.pull_request import PullRequest
from src.model.github.repository import Repository


class PullRequestEventAction(str, Enum):
    ASSIGNED = "assigned"
    AUTO_MERGE_DISABLED = "auto_merge_disabled"
    AUTO_MERGE_ENABLED = "auto_merge_enabled"
    CLOSED = "closed"
    CONVERTED_TO_DRAFT = "converted_to_draft"
    DEMILESTONED = "demilestoned"
    DEQUEUED = "dequeued"
    EDITED = "edited"
    ENQUEUED = "enqueued"
    LABELED = "labeled"
    LOCKED = "locked"
    MILESTONED = "milestoned"
    OPENED = "opened"
    READY_FOR_REVIEW = "ready_for_review"
    REOPENED = "reopened"
    REVIEW_REQUEST_REMOVED = "review_request_removed"
    EVIEW_REQUESTED = "review_requested"
    SYNCHRONIZE = "synchronize"
    UNASSIGNED = "unassigned"
    UNLABELED = "unlabeled"
    UNLOCKED = "unlocked"


class PullRequestEventInstallation(BaseModel):
    id: int


class PullRequestEvent(BaseModel):
    action: PullRequestEventAction
    number: int
    sender: Account
    pull_request: PullRequest
    repository: Repository
    installation: PullRequestEventInstallation
