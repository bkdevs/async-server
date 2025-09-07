from typing import Callable, Optional, Sequence, Union

from langchain_core.language_models import LanguageModelLike
from langchain_core.tools import BaseTool
from langchain_openai import ChatOpenAI
from langgraph.prebuilt.chat_agent_executor import StructuredResponseSchema
from langgraph.prebuilt.tool_node import ToolNode

from src.agent.agent_metadata import AgentMetadata
from src.prompt.chat_prompt import CHAT_SYSTEM_PROMPT
from src.tools.filesystem import ListFiles, ReadFile
from src.tools.git import GitGrep


class ChatAgentMetadata(AgentMetadata):
    """
    Chat agent parameters
    """

    def get_default_title(self) -> str:
        return "Gathering requirements"

    def get_input_message(self) -> str:
        return f"User inquiry: {self.config['user_message']}"

    def _get_name(self) -> str:
        return "chat-agent"

    def _get_model(self) -> LanguageModelLike:
        return ChatOpenAI(model="gpt-5", reasoning_effort="low")

    def _get_system_prompt(self) -> str:
        return CHAT_SYSTEM_PROMPT.format(
            project_overview=self.config["project"].overview,
            project_structure=self.config["project"].tree,
            repo_directory=self.config["repo_directory"],
        )

    def _get_tools(self) -> Union[Sequence[Union[BaseTool, Callable]], ToolNode]:
        return [ListFiles(), ReadFile(), GitGrep()]

    def _get_response_format(self) -> Optional[StructuredResponseSchema]:
        return None
