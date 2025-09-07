import os
from typing import Type

import aiofiles
from langchain_core.runnables import RunnableConfig
from pydantic import BaseModel, Field

from src.tools.async_tool import AsyncTool


class ReadFileInput(BaseModel):
    file_path: str = Field(description="Absolute path to the file to read")


class ReadFile(AsyncTool):
    name: str = "read_file"
    description: str = "Read complete contents of a file using UTF-8 encoding"
    args_schema: Type[BaseModel] = ReadFileInput

    async def _validate_input_async(self, tool_input: ReadFileInput, config: RunnableConfig):
        repo_directory = config.get("configurable").get("repo_directory")
        if repo_directory and not tool_input.file_path.startswith(repo_directory):
            raise ValueError(f"The given path is not absolute. It must start with {repo_directory}.")
        if not os.path.exists(tool_input.file_path):
            raise FileNotFoundError()

    async def _call_async(self, tool_input: ReadFileInput, config: RunnableConfig) -> str:
        async with aiofiles.open(tool_input.file_path, mode="r", encoding="utf-8") as file:
            contents = await file.read()
            return contents

    def _get_in_progress_title(self, tool_input: ReadFileInput, config: RunnableConfig) -> str:
        sanitized_path = self._sanitize_path(tool_input.file_path, config)
        return f"Reading {sanitized_path}"

    def _get_completed_title(self, tool_input: ReadFileInput, config: RunnableConfig) -> str:
        sanitized_path = self._sanitize_path(tool_input.file_path, config)
        return f"Read {sanitized_path}"
