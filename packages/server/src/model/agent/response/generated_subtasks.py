from pydantic import BaseModel, Field


class GeneratedSubtask(BaseModel):
    title: str = Field(description="Descriptive title for the subtask")
    steps: list[str] = Field(description="List of concrete, actionable steps for implementing this subtask")


class GeneratedSubtasks(BaseModel):
    subtasks: list[GeneratedSubtask] = Field(
        description="List of subtasks that break down the main task into actionable components"
    )
