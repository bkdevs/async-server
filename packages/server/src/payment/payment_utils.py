from datetime import datetime, timezone

from src.clients import get_firestore_client, get_stripe_client
from src.model.app import Profile, User
from src.model.payment import PaymentPlan, StripeCustomer
from src.payment.payment_constants import STANDARD_PRICE_LOOKUP_KEY


async def create_stripe_customer_async(user: User, profile: Profile) -> User:
    stripe_client = get_stripe_client()
    customer = await stripe_client.create_customer_async(profile.name, profile.email)

    firestore_client = get_firestore_client()
    update_user = await firestore_client.update_user_async(user.id, stripe_id=customer.id)
    await firestore_client.create_stripe_customer_async(
        StripeCustomer(
            id=customer.id,
            user_id=user.id,
        )
    )
    return update_user


async def update_payment_plan_async(stripe_id: str, payment_plan: PaymentPlan):
    firestore_client = get_firestore_client()
    stripe_customer = await firestore_client.get_stripe_customer_async(stripe_id)
    if not stripe_customer:
        raise ValueError(f"Stripe customer document does not exist for user with Stripe ID: {stripe_id}")

    user = await firestore_client.get_user_async(stripe_customer.user_id)
    await firestore_client.update_org_async(
        org_id=user.org_id,
        payment_plan=payment_plan,
        credits=payment_plan.default_credits,
        updated_at=datetime.now(timezone.utc),
    )


async def create_checkout_url_async(user_id: str, org_id: str, lookup_key: str = STANDARD_PRICE_LOOKUP_KEY) -> str:
    firestore_client = get_firestore_client()
    user = await firestore_client.get_user_async(user_id)
    if not user.stripe_id:
        profile = await firestore_client.get_profile_async(org_id, user_id)
        user = await create_stripe_customer_async(
            user=user,
            profile=profile,
        )

    stripe_client = get_stripe_client()
    prices = await stripe_client.list_prices_async(lookup_key)
    standard_price_id = prices.data[0].id
    checkout_session = await stripe_client.create_checkout_session_async(user.stripe_id, standard_price_id)
    return checkout_session.url


async def decrement_credit_async(org_id: str) -> int:
    firestore_client = get_firestore_client()
    org = await firestore_client.get_org_async(org_id)
    updated_credit = org.credits - 1
    await firestore_client.update_org_async(org_id, credits=updated_credit)
    return updated_credit
