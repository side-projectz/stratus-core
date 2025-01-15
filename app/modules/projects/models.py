from datetime import datetime
from uuid import UUID

from sqlmodel import Field, SQLModel

from app.utils import generate_timestamp, generate_uuid


class ProjectBase(SQLModel):
	path: str = Field(index=True, unique=True, min_length=1)
	name: str = Field(index=True, min_length=1)


class Project(ProjectBase, table=True):
	id: UUID = Field(default_factory=generate_uuid, primary_key=True)

	created_at: datetime = Field(default_factory=generate_timestamp)
	updated_at: datetime = Field(default_factory=generate_timestamp)


__all__ = [Project, ProjectBase]
