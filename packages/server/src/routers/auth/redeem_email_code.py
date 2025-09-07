from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, status
from firebase_admin import auth

from src.api.auth import RedeemEmailCodeRequest, RedeemEmailCodeResponse
from src.clients import get_firestore_client
from src.model.app import User
from src.model.auth import AuthStatus

router = APIRouter()


@router.post("/redeem-email-code", status_code=status.HTTP_200_OK)
async def redeem_email_code_async(request: RedeemEmailCodeRequest) -> RedeemEmailCodeResponse:
    firestore_client = get_firestore_client()
    email_code = await firestore_client.get_email_code_async(request.code)

    if email_code is None:
        raise HTTPException(status_code=400, detail="Invalid email code")

    if email_code.status != "pending":
        raise HTTPException(status_code=400, detail="Email code already used")

    if email_code.expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=400, detail="Email code expired")

    await firestore_client.update_email_code_async(email_code.id, status=AuthStatus.ACCEPTED)

    user = User(
        id=email_code.user_id,
        name=email_code.email,
        email=email_code.email,
    )
    await firestore_client.create_user_async(user)
    auth.update_user(email_code.user_id, email_verified=True)
    return RedeemEmailCodeResponse()
