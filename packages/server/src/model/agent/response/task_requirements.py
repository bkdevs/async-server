from pydantic import BaseModel, Field


class TaskRequirements(BaseModel):
    requirements: list[str] = Field(description="List of concrete and implementable requirements for the task")
