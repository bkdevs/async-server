from pydantic import BaseModel


class RedeemEmailCodeRequest(BaseModel):
    user_id: str
    code: str


class RedeemEmailCodeResponse(BaseModel):
    pass
