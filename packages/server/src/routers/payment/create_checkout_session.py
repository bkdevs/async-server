from fastapi import APIRouter, status

from src.api.payment import (
    CreateCheckoutSessionRequest,
    CreateCheckoutSessionResponse,
)
from src.payment.payment_utils import create_checkout_url_async

router = APIRouter()


@router.post("/create-checkout-session", status_code=status.HTTP_200_OK)
async def create_checkout_session_async(request: CreateCheckoutSessionRequest) -> CreateCheckoutSessionResponse:
    """
    Create a Stripe hosted customer portal session that lets your customers
    manage their subscriptions and billing details. Return the portal URL.
    """
    redirect_url = await create_checkout_url_async(
        user_id=request.user_id, org_id=request.org_id, lookup_key=request.price_lookup_key
    )
    return CreateCheckoutSessionResponse(redirect_url=redirect_url)
