import logging
import os

import resend

logger = logging.getLogger(__name__)


class EmailClient:
    """
    Resend wrapper
    """

    def __init__(self):
        if resend.api_key is None:
            resend.api_key = os.getenv("RESEND_API_KEY")

        self.verify_email_html = open("src/email/html/verify_email.html", "r").read()
        self.invite_people_html = open("src/email/html/invite_people.html", "r").read()

    def send_verify_email(self, email: str, code: str):
        params: resend.Emails.SendParams = {
            "from": "Async <no-reply@domain>",
            "to": [email],
            "subject": "Verify your email",
            "html": self.verify_email_html.replace("REPLACE_VERIFICATION_CODE", code),
        }

        try:
            email = resend.Emails.send(params)
        except Exception as e:
            logger.error(f"Failed to verify email: {e}")

    def send_invite_people(self, email: str, code: str, user_name: str, org_name: str):
        params: resend.Emails.SendParams = {
            "from": "Async <no-reply@domain>",
            "to": [email],
            "subject": f"{user_name} has invited you to join {org_name}",
            "html": (
                self.invite_people_html.replace("REPLACE_INVITE_CODE", code)
                .replace("REPLACE_USER_NAME", user_name)
                .replace("REPLACE_ORG_NAME", org_name)
            ),
        }

        try:
            email = resend.Emails.send(params)
        except Exception as e:
            logger.error(f"Failed to send invite: {e}")

    def send_contact_us_form(self, email: str):
        params: resend.Emails.SendParams = {
            "from": "Async <no-reply@domain",
            "to": [email, "email@domain"],
            "subject": "Async - Contact Us",
            "text": "Thank you for contacting us. We'll get back to you shortly.",
        }

        try:
            email = resend.Emails.send(params)
        except Exception as e:
            logger.error(f"Failed to send contact us: {e}")
