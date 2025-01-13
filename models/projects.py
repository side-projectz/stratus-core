import logging
from uuid import UUID
from utils import generate_uuid
from sqlmodel import Field, SQLModel, select

from models import Session, engine

logger = logging.getLogger("uvicorn")


class ProjectBase(SQLModel):
    path: str = Field(index=True, unique=True)


class Project(ProjectBase, table=True):
    id: UUID = Field(default_factory=generate_uuid, primary_key=True)
    name: str = Field(index=True)


class ProjectPublic(ProjectBase):
    id: UUID
    name: str


class ProjectCreate(ProjectBase):
    name: str


class ProjectUpdate(ProjectBase):
    id: UUID
    name: str
    path: str


def get_project(id: UUID):
    with Session(engine) as session:
        projects = session.exec(select(Project).where(Project.id == id)).first()
        return projects
