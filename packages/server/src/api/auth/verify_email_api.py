from pydantic import BaseModel


class VerifyEmailRequest(BaseModel):
    email: str
    user_id: str


class VerifyEmailResponse(BaseModel):
    pass
