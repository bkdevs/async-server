from typing import Optional

from pydantic import BaseModel

from src.model.auth import Invite


class RedeemInviteCodeRequest(BaseModel):
    code: str


class RedeemInviteCodeResponse(BaseModel):
    invite: Optional[Invite] = None
