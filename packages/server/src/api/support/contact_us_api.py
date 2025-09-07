from pydantic import BaseModel


class ContactUsRequest(BaseModel):
    email: str
    company: str
    role: str
    message: str


class ContactUsResponse(BaseModel):
    pass
