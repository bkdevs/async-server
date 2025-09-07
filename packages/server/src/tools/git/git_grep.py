import asyncio
from typing import Type

from langchain_core.runnables import RunnableConfig
from pydantic import BaseModel, Field

from src.tools.async_tool import AsyncTool


class GitGrepInput(BaseModel):
    pattern: str = Field(description="The search pattern to grep for")


class GitGrep(AsyncTool):
    name: str = "git_grep"
    description: str = "Search for patterns (case-insensitive) in files tracked by Git using grep"
    args_schema: Type[BaseModel] = GitGrepInput

    async def _validate_input_async(self, tool_input: GitGrepInput, config: RunnableConfig):
        pass

    async def _call_async(self, tool_input: GitGrepInput, config: RunnableConfig) -> list[str]:
        repo_directory = config.get("configurable").get("repo_directory")
        process = await asyncio.create_subprocess_exec(
            "git",
            "grep",
            "-i",
            "-I",
            tool_input.pattern,
            cwd=repo_directory,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, _ = await process.communicate()

        if process.returncode == 0:
            return stdout.decode().splitlines()
        else:
            return []

    def _get_in_progress_title(self, tool_input: GitGrepInput, config: RunnableConfig) -> str:
        return f"Searching for '{tool_input.pattern}'"

    def _get_completed_title(self, tool_input: GitGrepInput, config: RunnableConfig) -> str:
        return f"Found matches for '{tool_input.pattern}'"

    def _get_text(self, tool_input: GitGrepInput, response: list[str], config: RunnableConfig) -> str:
        if not response:
            return f"No matches found for pattern '{tool_input.pattern}'"
        return "\n".join(response)
