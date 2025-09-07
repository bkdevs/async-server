from pydantic import BaseModel, Field

from src.model import generate_id
from src.model.app.project import Language


class Project(BaseModel):
    id: str = Field(default_factory=generate_id)
    name: str
    repo: str
    default_branch: str = "main"
    description: str = ""
    overview: str = ""
    tree: str = ""
    languages: list[Language] = []
    vercel_project_id: str = ""
