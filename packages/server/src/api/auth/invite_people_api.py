from pydantic import BaseModel


class InvitePeopleRequest(BaseModel):
    user_id: str
    org_id: str
    emails: list[str]


class InvitePeopleResponse(BaseModel):
    pass
