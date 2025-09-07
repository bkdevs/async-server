from pydantic import BaseModel


class CreatePortalSessionRequest(BaseModel):
    org_id: str
    user_id: str


class CreatePortalSessionResponse(BaseModel):
    redirect_url: str
