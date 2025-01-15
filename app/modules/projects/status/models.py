from enum import Enum
from uuid import UUID
from app.utils import generate_uuid, generate_timestamp
from datetime import datetime
from sqlmodel import SQLModel, Field


class ProjectStatusEnum(str, Enum):
    QUEUE = "queue"
    PROCESSING = "processing"
    FAILED = "failed"
    SUCCESS = "success"


class ProjectStatusBase(SQLModel):
    project_id: UUID = Field(foreign_key="project.id")
    status: ProjectStatusEnum = Field(default=ProjectStatusEnum.QUEUE)


class ProjectStatus(ProjectStatusBase, table=True):
    id: UUID = Field(default_factory=generate_uuid, primary_key=True)

    created_at: datetime = Field(default_factory=generate_timestamp)
    updated_at: datetime = Field(default_factory=generate_timestamp)



__all__ =[ProjectStatus, ProjectStatusBase, ProjectStatusEnum]