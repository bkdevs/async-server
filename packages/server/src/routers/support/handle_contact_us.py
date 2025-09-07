from fastapi import APIRouter, status

from src.api.support import ContactUsRequest, ContactUsResponse
from src.clients import get_email_client, get_firestore_client
from src.model.support import Lead

router = APIRouter()


@router.post("/handle-contact-us", status_code=status.HTTP_200_OK)
async def handle_contact_us_async(request: ContactUsRequest) -> ContactUsResponse:
    lead = await get_firestore_client().create_lead_async(
        Lead(
            email=request.email,
            company=request.company,
            role=request.role,
            message=request.message,
        )
    )
    get_email_client().send_contact_us_form(lead.email)
    return ContactUsResponse()
