from fastapi import APIRouter, status

from src.api.auth import RedeemInviteCodeRequest, RedeemInviteCodeResponse
from src.clients import get_firestore_client

router = APIRouter()


@router.post("/redeem-invite-code", status_code=status.HTTP_200_OK)
async def redeem_invite_code_async(request: RedeemInviteCodeRequest) -> RedeemInviteCodeResponse:
    invite = await get_firestore_client().get_invite_async(request.code)
    if invite and invite.status == "pending":
        return RedeemInviteCodeResponse(invite=invite)
    else:
        return RedeemInviteCodeResponse(invite=None)
