from typing import Literal, Union

from pydantic import BaseModel

from src.model.google import JobType


class IndexProjectJobRequest(BaseModel):
    job_type: Literal[JobType.INDEX_PROJECT] = JobType.INDEX_PROJECT
    org_id: str
    project_id: str
    is_dev: bool


class ExecuteTaskJobRequest(BaseModel):
    job_type: Literal[JobType.EXECUTE_TASK] = JobType.EXECUTE_TASK
    org_id: str
    task_id: str
    is_dev: bool


class ReviseTaskJobRequest(BaseModel):
    job_type: Literal[JobType.REVISE_TASK] = JobType.REVISE_TASK
    org_id: str
    task_id: str
    is_dev: bool


ScheduleJobRequest = Union[IndexProjectJobRequest, ExecuteTaskJobRequest, ReviseTaskJobRequest]


class ScheduleJobResponse(BaseModel):
    pass
