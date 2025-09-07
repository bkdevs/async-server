from typing import Callable, Optional, Sequence, Union

from langchain_core.language_models import LanguageModelLike
from langchain_core.tools import BaseTool
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.prebuilt.chat_agent_executor import StructuredResponseSchema
from langgraph.prebuilt.tool_node import ToolNode

from src.agent.agent_metadata import AgentMetadata
from src.model.agent.response import TaskRequirements
from src.prompt.summarize_requirements_prompt import SUMMARIZE_REQUIREMENTS_PROMPT


class SummaryAgentMetadata(AgentMetadata):
    """
    Agent to summarize task given agent traces so far (from research and/or chat)
    """

    def get_default_title(self) -> str:
        return "Summarizing task"

    def get_input_message(self) -> str:
        return "Summarize the task"

    def _get_name(self) -> str:
        return "summary-agent"

    def _get_model(self) -> LanguageModelLike:
        return ChatGoogleGenerativeAI(model="gemini-2.5-flash")

    def _get_system_prompt(self) -> str:
        return SUMMARIZE_REQUIREMENTS_PROMPT

    def _get_tools(self) -> Union[Sequence[Union[BaseTool, Callable]], ToolNode]:
        return []

    def _get_response_format(self) -> Optional[StructuredResponseSchema]:
        return TaskRequirements
