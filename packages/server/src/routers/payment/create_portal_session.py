from fastapi import APIRouter, status

from src.api.payment import (
    CreatePortalSessionRequest,
    CreatePortalSessionResponse,
)
from src.clients import get_firestore_client, get_stripe_client
from src.payment.payment_utils import create_stripe_customer_async

router = APIRouter()


@router.post("/create-portal-session", status_code=status.HTTP_200_OK)
async def create_portal_session_async(request: CreatePortalSessionRequest) -> CreatePortalSessionResponse:
    """
    Create a Stripe hosted customer portal session that lets your customers
    manage their subscriptions and billing details. Return the portal URL.
    """
    firestore_client = get_firestore_client()
    user = await firestore_client.get_user_async(request.user_id)
    if not user.stripe_id:
        profile = await firestore_client.get_profile_async(request.org_id, request.user_id)
        user = await create_stripe_customer_async(
            user=user,
            profile=profile,
        )

    portal_session = await get_stripe_client().create_portal_session_async(user.stripe_id)
    return CreatePortalSessionResponse(redirect_url=portal_session.url)
