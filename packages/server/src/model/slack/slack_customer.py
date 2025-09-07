from pydantic import BaseModel


class SlackCustomer(BaseModel):
    id: str  # Slack ID
    user_id: str  # Async ID
