from pydantic import BaseModel

from src.model import compute_repository_doc_id


class Repository(BaseModel):
    full_name: str
    org_id: str
    project_id: str

    @property
    def id(self) -> str:
        """
        Firestore ID property
        """
        return compute_repository_doc_id(self.full_name)
