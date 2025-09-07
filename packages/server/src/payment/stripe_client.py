import os

import stripe

from src.payment.payment_constants import RETURN_URL, SUCCESS_URL


class StripeClient:
    def __init__(self):
        if stripe.api_key is None:
            stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

    async def create_customer_async(self, name: str, email: str) -> stripe.Customer:
        return await stripe.Customer.create_async(name=name, email=email)

    async def list_prices_async(self, lookup_key: str) -> list[stripe.Price]:
        return await stripe.Price.list_async(lookup_keys=[lookup_key])

    async def create_checkout_session_async(self, stripe_user_id: str, price_id: str) -> stripe.checkout.Session:
        return await stripe.checkout.Session.create_async(
            customer=stripe_user_id,
            line_items=[
                {
                    "price": price_id,
                    "quantity": 1,
                }
            ],
            mode="subscription",
            customer_update={"address": "auto"},
            automatic_tax={"enabled": True},
            success_url=SUCCESS_URL,
            cancel_url=RETURN_URL,
        )

    async def create_portal_session_async(self, stripe_user_id: str) -> stripe.billing_portal.Session:
        return await stripe.billing_portal.Session.create_async(
            customer=stripe_user_id,
            return_url=RETURN_URL,
        )

    def construct_webhook_event(self, body: bytes, signature: str, secret: str) -> stripe.Event:
        return stripe.Webhook.construct_event(
            payload=body,
            sig_header=signature,
            secret=secret,
        )
