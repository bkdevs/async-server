from pydantic import BaseModel


class StripeCustomer(BaseModel):
    id: str  # Stripe ID
    user_id: str  # Async ID
