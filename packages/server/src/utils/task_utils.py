from openai import AsyncOpenAI
from pydantic import BaseModel, Field

from src.model.agent.response import TaskRequirements
from src.model.app.project.project import Project


async def find_matching_project(projects: list[Project], task_description: str) -> list[Project]:
    class ProjectMatchResponse(BaseModel):
        project_ids: list[str] = Field(description="List of project IDs that best match the task description")

    project_overviews = {project.id: project.overview for project in projects}
    project_trees = {project.id: project.tree for project in projects}
    system_prompt = (
        "You are a scrum master, responsible for triaging tasks. Given a task description and a "
        "list of project overviews and file structures, identify which project(s) are most relevant "
        "for the task. Return the project ID(s) that best match the task requirements based on the "
        "project descriptions and context."
    )
    user_prompt = (
        "Find project ID(s) that best match the task description.\n"
        f"- project overviews: {project_overviews}\n"
        f"- project file structures: {project_trees}"
        f"- task description: {task_description}\n"
    )
    open_ai_client = AsyncOpenAI()
    response = await open_ai_client.responses.parse(
        model="gpt-4.1",
        input=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        text_format=ProjectMatchResponse,
    )
    matching_projects = response.output_parsed
    return [project for project in projects if project.id in matching_projects.project_ids]


async def generate_task_name_async(task_description: str) -> str:
    open_ai_client = AsyncOpenAI()
    prompt = f"Create a short desription (less than a sentence) of the Github issue: {task_description}"
    response = await open_ai_client.responses.create(
        model="gpt-4.1-mini",
        input=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
    )
    return response.output_text


def summarize_requirements(latest_message: str) -> TaskRequirements:
    requirements = []
    lines = latest_message.split("\n")

    for line in lines:
        if line.strip().startswith("- "):
            requirement = line.strip()[2:].strip()
            if requirement:
                requirements.append(requirement)

    return TaskRequirements(requirements=requirements)
