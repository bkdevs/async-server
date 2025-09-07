from typing import Callable, Optional, Sequence, Union

from langchain_core.language_models import LanguageModelLike
from langchain_core.tools import BaseTool
from langchain_openai import ChatOpenAI
from langgraph.prebuilt.chat_agent_executor import StructuredResponseSchema
from langgraph.prebuilt.tool_node import ToolNode

from src.agent.agent_metadata import AgentMetadata
from src.prompt.analyze_project_prompt import ANALYZE_PROJECT_PROMPT
from src.tools.filesystem import ListFiles, ReadFile
from src.tools.git import GitGrep


class AnalyzerAgentMetadata(AgentMetadata):
    """
    Analyzer agent parameters
    """

    def get_default_title(self) -> str:
        return "Analyzing project"

    def get_input_message(self) -> str:
        return (
            "Analyze the repository:\n"
            f"- Repo directory: {self.config['repo_directory']}\n"
            f"- File structure: {self.config['project'].tree}"
        )

    def _get_name(self) -> str:
        return "analyzer-agent"

    def _get_model(self) -> LanguageModelLike:
        return ChatOpenAI(model="gpt-5", reasoning_effort="high")

    def _get_system_prompt(self) -> str:
        return ANALYZE_PROJECT_PROMPT

    def _get_tools(self) -> Union[Sequence[Union[BaseTool, Callable]], ToolNode]:
        return [ReadFile(), ListFiles(), GitGrep()]

    def _get_response_format(self) -> Optional[StructuredResponseSchema]:
        return None
