from abc import ABC, abstractmethod
from typing import final

from langchain_core.runnables import RunnableConfig
from langchain_core.tools import ArgsSchema, BaseTool
from langgraph.config import get_stream_writer

from src.model.app.task import MessageEvent


class AsyncTool(BaseTool, ABC):
    """
    Base tool class for async application
    """

    @final
    async def _arun(self, config: RunnableConfig, *args: any, **kwargs: any) -> any:
        try:
            tool_input = self.args_schema(**kwargs)
            await self._validate_input_async(tool_input, config)
            response = await self._call_async(tool_input, config)
            await self._on_tool_completed_async(tool_input, response, config)
        except Exception as e:
            # re-raise so LLM can see the error
            raise e
        else:
            return response

    def _run(self, *args: any, **kwargs: any) -> any:
        raise NotImplementedError("AsyncTool only supports async execution. Use arun() instead of run().")

    @abstractmethod
    def _get_in_progress_title(self, tool_input: ArgsSchema, config: RunnableConfig) -> str:
        raise NotImplementedError

    @abstractmethod
    def _get_completed_title(self, tool_input: ArgsSchema, config: RunnableConfig) -> str:
        raise NotImplementedError

    @abstractmethod
    async def _validate_input_async(self, tool_input: ArgsSchema, config: RunnableConfig):
        raise NotImplementedError

    @abstractmethod
    async def _call_async(self, tool_input: ArgsSchema, config: RunnableConfig) -> any:
        raise NotImplementedError

    async def _on_tool_completed_async(self, tool_input: ArgsSchema, response: any, config: RunnableConfig):
        message_event = self._create_message_event(tool_input, response, config)
        get_stream_writer()(message_event)

    def _create_message_event(self, tool_input: ArgsSchema, response: any, config: RunnableConfig) -> MessageEvent:
        in_progress_title = self._get_in_progress_title(tool_input, config)
        completed_title = self._get_completed_title(tool_input, config)
        text = self._get_text(tool_input, response, config)
        preview = self._get_preview(tool_input, response, config)
        return MessageEvent(
            type=self.name,
            in_progress_title=in_progress_title,
            completed_title=completed_title,
            text=text,
            preview=preview,
        )

    def _get_text(self, tool_input: ArgsSchema, response: any, config: RunnableConfig) -> str:
        if isinstance(response, str) and response:
            return response
        return "Done"

    def _get_preview(self, tool_input: ArgsSchema, response: any, config: RunnableConfig) -> str:
        return self._get_text(tool_input, response, config)[:500]

    def _sanitize_path(self, path: str, config: RunnableConfig):
        if "configurable" not in config or "repo_directory" not in config["configurable"]:
            return path
        return path.replace(config["configurable"]["repo_directory"], "").lstrip("/")
