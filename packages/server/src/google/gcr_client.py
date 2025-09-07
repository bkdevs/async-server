from google.cloud import run_v2
from google.cloud.run_v2.types import CancelExecutionRequest, EnvVar, GetExecutionRequest, RunJobRequest
from src.api.task import (
    ExecuteTaskJobRequest,
    IndexProjectJobRequest,
    ReviseTaskJobRequest,
    ScheduleJobRequest,
)
from src.google.gcp_constants import JOB_NAME_PREFIX
from src.model.app.project import Language


class GcrClient:
    """
    Wrapper client for Google Cloud Run
    """

    def __init__(self):
        self.execution_client = run_v2.ExecutionsAsyncClient()
        self.job_client = run_v2.JobsAsyncClient()

    async def run_job_async(self, request: ScheduleJobRequest, languages: list[Language]) -> str:
        job_request = None
        match request:
            case IndexProjectJobRequest():
                job_request = self._get_index_project_job_request(request, languages)
            case ExecuteTaskJobRequest():
                job_request = self._get_execute_task_job_request(request, languages)
            case ReviseTaskJobRequest():
                job_request = self._get_revise_task_job_request(request, languages)

        operation = await self.job_client.run_job(request=job_request)
        return operation.metadata.name

    async def get_execution_async(self, execution_id: str) -> run_v2.Execution:
        get_execution_request = GetExecutionRequest(name=execution_id)
        return await self.execution_client.get_execution(request=get_execution_request)

    async def cancel_job_async(self, execution_id: str) -> None:
        cancel_request = CancelExecutionRequest(name=execution_id)
        await self.execution_client.cancel_execution(request=cancel_request)

    def _get_index_project_job_request(
        self, request: IndexProjectJobRequest, languages: list[Language]
    ) -> RunJobRequest:
        return RunJobRequest(
            name=self._get_job_endpoint(languages),
            overrides=RunJobRequest.Overrides(
                container_overrides=[
                    RunJobRequest.Overrides.ContainerOverride(
                        env=[
                            EnvVar(name="COMMAND_MODULE", value="src.index_project"),
                            EnvVar(name="ORG_ID", value=request.org_id),
                            EnvVar(name="PROJECT_ID", value=request.project_id),
                            EnvVar(name="IS_DEV", value=str(request.is_dev)),
                        ]
                    )
                ]
            ),
        )

    def _get_execute_task_job_request(self, request: ExecuteTaskJobRequest, languages: list[Language]) -> RunJobRequest:
        return RunJobRequest(
            name=self._get_job_endpoint(languages),
            overrides=RunJobRequest.Overrides(
                container_overrides=[
                    RunJobRequest.Overrides.ContainerOverride(
                        env=[
                            EnvVar(name="COMMAND_MODULE", value="src.execute_task"),
                            EnvVar(name="ORG_ID", value=request.org_id),
                            EnvVar(name="TASK_ID", value=request.task_id),
                            EnvVar(name="IS_DEV", value=str(request.is_dev)),
                        ]
                    )
                ]
            ),
        )

    def _get_revise_task_job_request(self, request: ReviseTaskJobRequest, languages: list[Language]) -> RunJobRequest:
        return RunJobRequest(
            name=self._get_job_endpoint(languages),
            overrides=RunJobRequest.Overrides(
                container_overrides=[
                    RunJobRequest.Overrides.ContainerOverride(
                        env=[
                            EnvVar(name="COMMAND_MODULE", value="src.revise_task"),
                            EnvVar(name="ORG_ID", value=request.org_id),
                            EnvVar(name="TASK_ID", value=request.task_id),
                            EnvVar(name="IS_DEV", value=str(request.is_dev)),
                        ]
                    )
                ]
            ),
        )

    def _get_job_endpoint(self, languages: list[Language]) -> str:
        # pylint: disable=unsupported-membership-test
        if Language.JAVASCRIPT in languages or Language.TYPESCRIPT in languages:
            return f"{JOB_NAME_PREFIX}/invoke-js"
        elif Language.DART in languages:
            return f"{JOB_NAME_PREFIX}/invoke-dart"
        else:
            return f"{JOB_NAME_PREFIX}/invoke"
