import httpcore
import httpx
from pydantic import BaseModel

from src.api.task import ExecuteTaskJobRequest, IndexProjectJobRequest, ReviseTaskJobRequest
from src.async_module.async_constants import LOCAL_URL, PROD_URL


class AsyncClient:
    """
    Client to call Async endpoints
    """

    async def invoke_index_project_job_async(self, org_id: str, project_id: str, is_dev: bool = False):
        payload = IndexProjectJobRequest(org_id=org_id, project_id=project_id, is_dev=is_dev)
        return await self._invoke_async("task/schedule-job", payload, is_dev)

    async def invoke_execute_task_job_async(self, org_id: str, task_id: str, is_dev: bool = False):
        payload = ExecuteTaskJobRequest(org_id=org_id, task_id=task_id, is_dev=is_dev)
        return await self._invoke_async("task/schedule-job", payload, is_dev)

    async def invoke_revise_task_job_async(self, org_id: str, task_id: str, is_dev: bool = False):
        payload = ReviseTaskJobRequest(org_id=org_id, task_id=task_id, is_dev=is_dev)
        return await self._invoke_async("task/schedule-job", payload, is_dev)

    async def _invoke_async(self, route: str, payload: BaseModel, is_dev: bool = False) -> dict:
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.post(url=f"{self._get_base_url(is_dev)}/{route}", json=payload.model_dump())
                if response.status_code != 200:
                    raise httpx.HTTPStatusError(
                        message=f"Failed to invoke {route}: {response.text}",
                        request=response.request,
                        response=response,
                    )
                return response.json()
        except (httpcore.ReadTimeout, httpcore.ConnectTimeout, httpx.TimeoutException):
            pass

    def _get_base_url(self, is_dev: bool) -> str:
        if is_dev:
            return LOCAL_URL
        return PROD_URL
