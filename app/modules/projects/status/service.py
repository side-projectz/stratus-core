from uuid import UUID
from sqlmodel import select
from models import Session, engine
from datetime import datetime, timezone

from ..models import Project
from .models import ProjectStatus
from .schemas import ProjectStatusSchema


class ProjectStatusService:
    def __init__(self):
        pass

    def get_project_status(self, id: UUID) -> ProjectStatusSchema.ProjectStatusRead:
        with Session(engine) as session:
            project_status = session.exec(
                select(ProjectStatus).where(ProjectStatus.id == id)
            ).first()
            if not project_status:
                raise ValueError("Project status not found.")
        return ProjectStatusSchema.ProjectStatusRead(
            id=project_status.id,
            project_id=project_status.project_id,
            status=project_status.status,
        )

    def get_project_status_by_project_id(
        self,
        project_id: UUID,
    ) -> ProjectStatusSchema.ProjectStatusList:
        with Session(engine) as session:
            project = session.exec(
                select(Project).where(Project.id == project_id)
            ).first()
            if not project:
                raise ValueError("Project not found.")

            project_status = session.exec(
                select(ProjectStatus).where(ProjectStatus.project_id == project_id)
            ).first()
        if not project_status:
            # raise ValueError("Project status not found.")
            return None
        return ProjectStatusSchema.ProjectStatusRead(
            id=project_status.id,
            project_id=project_status.project_id,
            status=project_status.status,
        )

    def create_project_status(
        self, project_id: UUID, status: str
    ) -> ProjectStatusSchema.ProjectStatusRead:
        with Session(engine) as session:
            project = session.exec(
                select(Project).where(Project.id == project_id)
            ).first()
            if not project:
                raise ValueError("Project not found.")

            project_status = ProjectStatus(project_id=project_id, status=status)
            session.add(project_status)
            session.commit()
            session.refresh(project_status)
            return ProjectStatusSchema.ProjectStatusRead(
                id=project_status.id,
                project_id=project_status.project_id,
                status=project_status.status,
            )

    def update_project_status(
        self, project_status_id: UUID, status: str
    ) -> ProjectStatusSchema.ProjectStatusRead:
        with Session(engine) as session:
            project_status = session.get(ProjectStatus, project_status_id)
            if not project_status:
                raise ValueError("Project status not found.")
            project_status.status = status
            project_status.updated_at = datetime.now(timezone.utc)
            session.commit()
            session.refresh(project_status)
            return ProjectStatusSchema.ProjectStatusRead(
                id=project_status.id,
                project_id=project_status.project_id,
                status=project_status.status,
            )


__all__ = [ProjectStatusService]
