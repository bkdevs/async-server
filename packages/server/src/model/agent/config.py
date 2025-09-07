from typing_extensions import TypedDict

from src.model.agent.response import TaskRequirements
from src.model.app import Org
from src.model.app.project import Project
from src.model.app.task import Task


class AsyncConfig(TypedDict, total=False):
    """
    Class containing immutable configuration that contains session information
    """

    thread_id: str
    """
    Unique ID assigned to each checkpoint saved by a checkpointer LangGraph concept
    """

    repo_directory: str
    """
    Absolute path to the cloned repository
    """

    org: Org
    """
    Organization model
    """

    project: Project
    """
    Project model
    """

    task: Task
    """
    Task model
    """

    task_id: str
    """
    Task ID
    """

    user_id: str
    """
    User ID
    """

    user_message: str
    """
    User message
    """

    is_dev: bool
    """
    Boolean to tell whether the request is for development
    """

    task_requirements: TaskRequirements
    """
    Requirements of the task
    """
