from datetime import datetime, timezone
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field

from src.model import generate_id
from src.model.payment import PaymentPlan


class OrgType(str, Enum):
    USER = "user"
    ORGANIZATION = "organization"


class Org(BaseModel):
    id: str = Field(default_factory=generate_id)
    name: str

    # Github
    github_installation_id: int
    github_account_type: OrgType = OrgType.ORGANIZATION
    github_account_name: Optional[str] = ""
    github_avatar_url: Optional[str] = ""
    onboarded: bool = False

    # Vercel
    vercel_access_token: Optional[str] = ""
    vercel_team_id: Optional[str] = ""

    # Payment
    payment_plan: PaymentPlan = PaymentPlan.FREE
    credits: int = 10

    # Date
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
