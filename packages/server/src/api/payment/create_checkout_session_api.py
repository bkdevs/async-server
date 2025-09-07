from pydantic import BaseModel

from src.payment.payment_constants import STANDARD_PRICE_LOOKUP_KEY


class CreateCheckoutSessionRequest(BaseModel):
    org_id: str
    user_id: str
    price_lookup_key: str = STANDARD_PRICE_LOOKUP_KEY


class CreateCheckoutSessionResponse(BaseModel):
    redirect_url: str
