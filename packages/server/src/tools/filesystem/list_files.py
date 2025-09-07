import asyncio
import os
from typing import Type

from langchain_core.runnables import RunnableConfig
from pydantic import BaseModel, Field

from src.tools.async_tool import AsyncTool


class ListFilesInput(BaseModel):
    directory_path: str = Field(description="Absolute path to the directory")


class ListFiles(AsyncTool):
    name: str = "list_files"
    description: str = "List all files in a directory"
    args_schema: Type[BaseModel] = ListFilesInput

    async def _validate_input_async(self, tool_input: ListFilesInput, config: RunnableConfig):
        repo_directory = config.get("configurable").get("repo_directory")
        if repo_directory and not tool_input.directory_path.startswith(repo_directory):
            raise ValueError(f"The given path is not absolute. It must start with {repo_directory}.")
        if not os.path.exists(tool_input.directory_path):
            raise FileNotFoundError(f"Directory {tool_input.directory_path} does not exist")
        if not os.path.isdir(tool_input.directory_path):
            raise NotADirectoryError(f"{tool_input.directory_path} is not a directory")

    async def _call_async(self, tool_input: ListFilesInput, config: RunnableConfig) -> list[str]:
        file_list = []
        items = await asyncio.to_thread(os.listdir, tool_input.directory_path)
        for item in items:
            item_path = os.path.join(tool_input.directory_path, item)
            file_list.append(item_path)
        return file_list

    def _get_in_progress_title(self, tool_input: ListFilesInput, config: RunnableConfig) -> str:
        sanitized_path = self._sanitize_path(tool_input.directory_path, config)
        sanitized_path = sanitized_path if sanitized_path else "~"
        return f"Listing {sanitized_path}"

    def _get_completed_title(self, tool_input: ListFilesInput, config: RunnableConfig) -> str:
        sanitized_path = self._sanitize_path(tool_input.directory_path, config)
        sanitized_path = sanitized_path if sanitized_path else "~"
        return f"Listed {sanitized_path}"

    def _get_text(self, tool_input: ListFilesInput, response: list[str], config: RunnableConfig) -> str:
        return "\n".join([self._sanitize_path(file_path, config) for file_path in response])
