from uuid import UUID

from pydantic import BaseModel, Field

from .status.models import ProjectStatusEnum


class ProjectSchemas(BaseModel):
	class ProjectCreate(BaseModel):
		name: str = Field(..., min_length=1)
		path: str = Field(..., min_length=1)

	class ProjectDetails(BaseModel):
		id: UUID
		name: str
		path: str
		status: ProjectStatusEnum | None

	class ProjectRead(BaseModel):
		id: UUID
		name: str
		path: str

	class ProjectDelete(BaseModel):
		id: UUID

	class ProjectUpdate(BaseModel):
		name: str | None = Field(..., min_length=1)

	class ProjectUpdatePath(BaseModel):
		path: str = Field(..., min_length=1)

	class ProjectList(BaseModel):
		projects: list["ProjectSchemas.ProjectRead"] = []


__all__ = [ProjectSchemas]
