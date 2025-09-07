import logging
import os
from typing import Optional

import stripe
from fastapi import APIRouter, Header, HTTPException, Request, Response, status

from src.clients import get_stripe_client
from src.model.payment import PaymentPlan
from src.payment.payment_utils import update_payment_plan_async

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/handle-stripe-events", status_code=status.HTTP_200_OK)
async def handle_stripe_events_async(
    request: Request, stripe_signature: Optional[str] = Header(None, alias="stripe-signature")
) -> Response:
    webhook_secret = os.environ.get("STRIPE_WEBHOOK_SECRET")
    if not webhook_secret:
        logger.error("Webhook secret not available")
        raise HTTPException(status_code=500, detail="Invalid state")
    if not stripe_signature:
        logger.error("Missing stripe signature")
        raise HTTPException(status_code=400, detail="Missing signature")

    body = await request.body()
    try:
        event = get_stripe_client().construct_webhook_event(body, stripe_signature, webhook_secret)
    except ValueError as e:
        logger.error(f"Invalid payload: {e}")
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError as e:
        logger.error(f"Invalid signature: {e}")
        raise HTTPException(status_code=400, detail="Invalid signature")

    event_type = event["type"]
    if event_type == "customer.subscription.created":
        subscription = event["data"]["object"]
        stripe_id = subscription["customer"]
        await update_payment_plan_async(stripe_id, PaymentPlan.STANDARD)
        logger.info(f"Subscription created for {stripe_id}")
    elif event_type == "customer.subscription.deleted":
        subscription = event["data"]["object"]
        stripe_id = subscription["customer"]
        await update_payment_plan_async(stripe_id, PaymentPlan.FREE)
        logger.info(f"Subscription cancelled for {stripe_id}")
    return Response()
