import logging
from uuid import UUID, uuid4
from enum import Enum
from datetime import datetime, timezone
from sqlmodel import Field, SQLModel
from models import Session, engine

logger = logging.getLogger("uvicorn")


class ProjectStatusEnum(str, Enum):
    QUEUE = "queue"
    PROCESSING = "processing"
    FAILED = "failed"
    SUCCESS = "success"


class ProjectStatusBase(SQLModel):
    project_id: UUID = Field(foreign_key="project.id")
    status: ProjectStatusEnum = Field(default=ProjectStatusEnum.QUEUE)
    created_at: datetime = Field(default=datetime.now(timezone.utc))
    updated_at: datetime = Field(default=datetime.now(timezone.utc))


class ProjectStatus(ProjectStatusBase, table=True):
    id: UUID = Field(default=uuid4(), primary_key=True)


class UpdateProjectStatus(SQLModel):
    id: UUID = Field(default=uuid4())
    status: ProjectStatusEnum
    updated_at: datetime = Field(default=datetime.now(timezone.utc))


def update_project_status(project_status_id: UUID, _status: ProjectStatusEnum):
    with Session(engine) as session:
        ps_db = session.get(ProjectStatus, project_status_id)

        ps_data = ProjectStatus(
            id=ps_db.id,
            project_id=ps_db.project_id,
            created_at=ps_db.created_at,
            status=_status,
        )

        ps_db.sqlmodel_update(ps_data)

        session.add(ps_db)
        session.commit()
        session.refresh(ps_db)
        logger.info(f"Project Status Updated to {ps_db.status}")
        return ps_db
