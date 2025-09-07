from fastapi import APIRouter, HTTPException, status

from src.agent import OutputFormatter
from src.api.task import CreateSubtasksRequest, CreateSubtasksResponse
from src.clients import get_firestore_client
from src.model.agent.response import GeneratedSubtasks
from src.model.app.task import Subtask

router = APIRouter()


@router.post("/create-subtasks", status_code=status.HTTP_200_OK)
async def create_subtasks_async(request: CreateSubtasksRequest) -> CreateSubtasksResponse:
    try:
        formatter = OutputFormatter()
        result = await formatter.format_output_async(request.subtasks_json_str, GeneratedSubtasks)

        firestore_client = get_firestore_client()
        await firestore_client.delete_subtask_async(request.org_id, request.task_id, request.subtask_id)

        subtasks = []
        for generated_subtask in result.subtasks:
            subtask = Subtask(
                title=generated_subtask.title,
                steps=generated_subtask.steps,
            )
            await firestore_client.create_subtask_async(request.org_id, request.task_id, subtask)
            subtasks.append(subtask)
        return CreateSubtasksResponse(subtasks=subtasks)
    except ValueError:
        raise HTTPException(status_code=500, detail=f"Failed to format JSON: {request.subtasks_json_str}")
