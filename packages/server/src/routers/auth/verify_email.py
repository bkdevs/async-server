from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, status

from src.api.auth import VerifyEmailRequest, VerifyEmailResponse
from src.clients import get_email_client, get_firestore_client
from src.model.auth import AuthStatus, EmailCode

router = APIRouter()


@router.post("/verify-email", status_code=status.HTTP_200_OK)
async def verify_email_async(request: VerifyEmailRequest) -> VerifyEmailResponse:
    email_code = await get_firestore_client().create_email_code_async(
        EmailCode(
            email=request.email,
            user_id=request.user_id,
            status=AuthStatus.PENDING,
            created_at=datetime.now(timezone.utc),
            expires_at=datetime.now(timezone.utc) + timedelta(minutes=15),
        )
    )
    get_email_client().send_verify_email(request.email, email_code.code)
    return VerifyEmailResponse()
