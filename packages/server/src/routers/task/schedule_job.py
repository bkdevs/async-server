from fastapi import APIRouter, BackgroundTasks, status

from src.api.task import (
    ExecuteTaskJobRequest,
    IndexProjectJobRequest,
    ReviseTaskJobRequest,
    ScheduleJobRequest,
    ScheduleJobResponse,
)
from src.clients import get_firestore_client, get_gcr_client
from src.execute_task import execute_task_async
from src.index_project import index_project_async
from src.model.app.project import Project
from src.payment.payment_utils import decrement_credit_async
from src.revise_task import revise_task_async

router = APIRouter()


@router.post("/schedule-job", status_code=status.HTTP_200_OK)
async def schedule_job_async(request: ScheduleJobRequest, background_tasks: BackgroundTasks) -> ScheduleJobResponse:
    if request.is_dev:
        match request:
            case IndexProjectJobRequest():
                background_tasks.add_task(
                    index_project_async,
                    request.org_id,
                    request.project_id,
                    request.is_dev,
                )
            case ExecuteTaskJobRequest():
                background_tasks.add_task(
                    execute_task_async,
                    request.org_id,
                    request.task_id,
                    request.is_dev,
                )
            case ReviseTaskJobRequest():
                background_tasks.add_task(
                    revise_task_async,
                    request.org_id,
                    request.task_id,
                    request.is_dev,
                )
        return ScheduleJobResponse()

    if isinstance(request, ExecuteTaskJobRequest):
        await decrement_credit_async(request.org_id)

    project = await _get_project_async(request)
    await get_gcr_client().run_job_async(request, project.languages)
    return ScheduleJobResponse()


async def _get_project_async(request: ScheduleJobRequest) -> Project:
    firestore_client = get_firestore_client()
    if hasattr(request, "project_id") and request.project_id:
        return await firestore_client.get_project_async(request.org_id, request.project_id)

    task = await firestore_client.get_task_async(request.org_id, request.task_id)
    return await firestore_client.get_project_async(request.org_id, task.project_id)
