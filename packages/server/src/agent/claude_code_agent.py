import json
import logging
import os
from dataclasses import asdict
from typing import Optional

from claude_code_sdk.query import query
from claude_code_sdk.types import ClaudeCodeOptions, PermissionMode

logger = logging.getLogger(__name__)


class ClaudeCodeAgent:
    """
    Cluade Code wrapper
    """

    def __init__(
        self,
        repo_directory: str,
        *,
        system_prompt: str | None = None,
        append_system_prompt: str | None = None,
        model: str | None = None,
        permission_mode: PermissionMode = "acceptEdits",
        verbose: bool = False,
    ):
        self.repo_directory = repo_directory
        self.system_prompt = system_prompt
        self.append_system_prompt = append_system_prompt
        self.model = model
        self.permission_mode = permission_mode
        self.verbose = verbose

    async def create_claude_md_async(self):
        if os.path.exists(f"{self.repo_directory}/CLAUDE.md"):
            return
        await self.run_async("/init")

    async def run_async(self, prompt: str, allowed_tools: list[str] = ["Read", "Write", "Bash"]) -> Optional[str]:
        last_message = None
        options = ClaudeCodeOptions(
            max_turns=200,
            cwd=self.repo_directory,
            system_prompt=self.system_prompt,
            append_system_prompt=self.append_system_prompt,
            model=self.model,
            allowed_tools=allowed_tools,
            permission_mode=self.permission_mode,
        )
        async for message in query(prompt=prompt, options=options):
            if self.verbose:
                logger.debug(json.dumps(asdict(message), indent=4))
            last_message = message

        if not last_message:
            return None
        if last_message.subtype != "success":
            return None
        return last_message.result
