from typing import Callable, Optional, Sequence, Union

from langchain_core.language_models import LanguageModelLike
from langchain_core.tools import BaseTool
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.prebuilt.chat_agent_executor import StructuredResponseSchema
from langgraph.prebuilt.tool_node import ToolNode

from src.agent.agent_metadata import AgentMetadata
from src.model.agent.response import TaskResearchOutput
from src.prompt.research_task_prompt import RESEARCH_TASK_PROMPT
from src.tools.filesystem import ListFiles, ReadFile
from src.tools.git import GitGrep


class ResearchAgentMetadata(AgentMetadata):
    """
    Research agent parameters
    """

    def get_default_title(self) -> str:
        return "Researching task"

    def get_input_message(self) -> str:
        return (
            "Analyze the given task:\n"
            f"- Task description: {self.config['task'].get_ingested_info()}\n"
            f"- Repo directory: {self.config['repo_directory']}\n"
            f"- Project overview: {self.config['project'].overview}\n"
            f"- File structure: {self.config['project'].tree}"
        )

    def _get_name(self) -> str:
        return "research-agent"

    def _get_model(self) -> LanguageModelLike:
        return ChatGoogleGenerativeAI(model="gemini-2.5-pro")

    def _get_system_prompt(self) -> str:
        return RESEARCH_TASK_PROMPT

    def _get_tools(self) -> Union[Sequence[Union[BaseTool, Callable]], ToolNode]:
        return [ListFiles(), ReadFile(), GitGrep()]

    def _get_response_format(self) -> Optional[StructuredResponseSchema]:
        return TaskResearchOutput
