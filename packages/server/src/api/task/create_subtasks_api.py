from pydantic import BaseModel

from src.model.app.task import Subtask


class CreateSubtasksRequest(BaseModel):
    org_id: str
    task_id: str
    subtask_id: str
    subtasks_json_str: str
    is_dev: bool = False


class CreateSubtasksResponse(BaseModel):
    subtasks: list[Subtask]
