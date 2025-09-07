# cspell:disable

from abc import ABC, abstractmethod
from typing import Callable, Optional, Sequence, Union

from langchain_core.language_models import LanguageModelLike
from langchain_core.tools import BaseTool
from langgraph.graph.graph import CompiledGraph
from langgraph.prebuilt import create_react_agent
from langgraph.prebuilt.chat_agent_executor import StructuredResponseSchema
from langgraph.prebuilt.tool_node import ToolNode
from langgraph.types import Checkpointer

from src.model.agent import AsyncConfig


class AgentMetadata(ABC):
    """
    Class that stores agent parameters
    """

    def __init__(self, config: Optional[AsyncConfig] = None):
        self.config = config or {}

    def create_agent(self, checkpointer: Optional[Checkpointer] = None) -> CompiledGraph:
        return create_react_agent(
            model=self._get_model(),
            tools=self._get_tools(),
            prompt=self._get_system_prompt(),
            config_schema=AsyncConfig,
            checkpointer=checkpointer,
            name=self._get_name(),
            response_format=self._get_response_format(),
        )

    @abstractmethod
    def get_default_title(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def get_input_message(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def _get_name(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def _get_model(self) -> LanguageModelLike:
        raise NotImplementedError

    @abstractmethod
    def _get_system_prompt(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def _get_tools(self) -> Union[Sequence[Union[BaseTool, Callable]], ToolNode]:
        raise NotImplementedError

    @abstractmethod
    def _get_response_format(self) -> Optional[StructuredResponseSchema]:
        raise NotImplementedError
