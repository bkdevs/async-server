from pydantic import BaseModel


class ImportIssuesRequest(BaseModel):
    user_id: str
    org_id: str
    is_dev: bool = False


class ImportIssuesResponse(BaseModel):
    pass
