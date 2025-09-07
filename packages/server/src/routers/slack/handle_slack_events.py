import logging
from typing import Optional

from fastapi import APIRouter, Header, Request, Response, status

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/handle-slack-events", status_code=status.HTTP_200_OK)
async def handle_slack_events_async(
    request: Request,
    x_slack_signature: Optional[str] = Header(None, alias="X-Slack-Signature"),
    x_slack_request_timestamp: Optional[str] = Header(None, alias="X-Slack-Request-Timestamp"),
) -> Response:
    """
    Handle Slack webhook events.

    This endpoint receives Slack webhook events but currently has minimal implementation.
    Add specific Slack event handling logic as needed.
    """

    # Get the request body
    body = await request.body()

    # For now, just log that we received a Slack event
    logger.info(f"Received Slack event with signature: {x_slack_signature}, body length: {len(body)}")

    # TODO: Add Slack signature verification
    # TODO: Parse Slack event payload
    # TODO: Handle specific Slack event types

    # Return 200 to acknowledge receipt
    return Response(status_code=200)
