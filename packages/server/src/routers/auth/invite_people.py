import hashlib

from fastapi import APIRouter, status

from src.api.auth import InvitePeopleRequest, InvitePeopleResponse
from src.clients import get_email_client, get_firestore_client
from src.model.auth import AuthStatus, Invite

router = APIRouter()


@router.post("/invite-people", status_code=status.HTTP_200_OK)
async def invite_people_async(request: InvitePeopleRequest) -> InvitePeopleResponse:
    firestore_client = get_firestore_client()
    org = await firestore_client.get_org_async(request.org_id)
    profile = await firestore_client.get_profile_async(request.org_id, request.user_id)

    invites = [
        Invite(
            id=hashlib.sha256(email.encode()).hexdigest(),
            email=email,
            org_id=request.org_id,
            org_name=org.name,
            from_user_name=profile.name,
            status=AuthStatus.PENDING,
        )
        for email in request.emails
    ]
    await firestore_client.create_invites_async(invites)

    email_client = get_email_client()
    for invite in invites:
        email_client.send_invite_people(invite.email, invite.code, profile.name, org.name)
    return InvitePeopleResponse()
