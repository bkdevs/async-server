import hashlib
import hmac
import json
import os
from typing import Optional

from fastapi import APIRouter, Header, HTTPException, Request, status
from fastapi.security import HTTPBearer

from src.github.handle_issue_comment import handle_issue_comment_async
from src.github.handle_issues import handle_issues_async
from src.github.handle_pull_request import handle_pull_request_async
from src.github.handle_push import handle_push_async
from src.model.github import IssueCommentEvent, IssuesEvent, PullRequestEvent, PushEvent

router = APIRouter()
bearer_scheme = HTTPBearer()


@router.post("/handle-github-events", status_code=status.HTTP_200_OK)
async def handle_github_events_async(
    request: Request,
    x_github_event: Optional[str] = Header(None, alias="X-GitHub-Event"),
    x_hub_signature_256: Optional[str] = Header(None, alias="X-Hub-Signature-256"),
):
    payload = await request.body()
    _verify_signature(payload, x_hub_signature_256, os.environ["GITHUB_WEBHOOK_SECRET"])

    try:
        data = json.loads(payload.decode("utf-8"))
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON payload")

    match x_github_event:
        case "issues":
            await handle_issues_async(IssuesEvent(**data))
        case "issue_comment":
            await handle_issue_comment_async(IssueCommentEvent(**data))
        case "pull_request":
            await handle_pull_request_async(PullRequestEvent(**data))
        case "push":
            await handle_push_async(PushEvent(**data))
        case _:
            pass


def _verify_signature(payload: bytes, signature: str, secret: str):
    """
    https://docs.github.com/en/webhooks/using-webhooks/validating-webhook-deliveries
    """
    if not signature:
        return False

    if not signature.startswith("sha256="):
        return False

    hash_object = hmac.new(secret.encode("utf-8"), payload, hashlib.sha256)
    expected_signature = "sha256=" + hash_object.hexdigest()
    if not hmac.compare_digest(expected_signature, signature):
        raise HTTPException(status_code=403, detail="Invalid signature")
