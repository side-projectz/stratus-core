from uuid import UUID
from sqlmodel import select
from models import Session, engine
from datetime import datetime, timezone


from app.utils.git import is_git_repo
from .models import Project
from .schemas import ProjectSchemas
from .status import ProjectStatusService, ProjectStatusEnum, ProjectStatus

project_status_service = ProjectStatusService()


class ProjectService:
    def __init__(self):
        pass

    def get_project(self, id: UUID) -> ProjectSchemas.ProjectDetails:
        with Session(engine) as session:
            project = session.exec(select(Project).where(Project.id == id)).first()
            if not project:
                raise ValueError("Project not found.")

        project_status = project_status_service.get_project_status_by_project_id(
            project_id=id
        )
        status = project_status.status if project_status else None
        return ProjectSchemas.ProjectDetails(
            id=project.id,
            name=project.name,
            path=project.path,
            status=status,
        )

    def get_project_list(
        self,
        offset: int = 0,
        limit: int = 100,
    ) -> ProjectSchemas.ProjectList:
        with Session(engine) as session:
            projects = session.exec(select(Project).offset(offset).limit(limit)).all()
            projects_read = [
                ProjectSchemas.ProjectRead.model_validate(p, from_attributes=True)
                for p in projects
            ]
            return ProjectSchemas.ProjectList(projects=projects_read)

    def get_project_count() -> int:
        with Session(engine) as session:
            return session.exec(select(Project)).count()

    def create_project(
        self,
        project_data: ProjectSchemas.ProjectCreate,
    ) -> ProjectSchemas.ProjectDetails:
        is_git_repo(project_data.path)
        with Session(engine) as session:
            existing = session.exec(
                select(Project).where(Project.path == project_data.path)
            ).first()
            if existing:
                raise ValueError("Project path already exists.")
            db_project = Project(**project_data.model_dump())
            session.add(db_project)
            session.commit()
            session.refresh(db_project)

        status = project_status_service.create_project_status(
            project_id=db_project.id, status=ProjectStatusEnum.QUEUE
        )

        return ProjectSchemas.ProjectDetails(
            id=db_project.id,
            name=db_project.name,
            path=db_project.path,
            status=status.status if status else None,
        )

    def update_project(
        self, project_id: UUID, project_data: ProjectSchemas.ProjectUpdate
    ) -> ProjectSchemas.ProjectRead:
        with Session(engine) as session:
            db_project = session.get(Project, project_id)
            if not db_project:
                raise ValueError("Project not found.")

            db_project.name = project_data.name
            db_project.updated_at = datetime.now(timezone.utc)
            session.commit()
            session.refresh(db_project)
            return ProjectSchemas.ProjectRead(
                id=db_project.id, name=db_project.name, path=db_project.path
            )

    def delete_project(self, project_id: UUID):
        with Session(engine) as session:
            db_project = session.get(Project, project_id)
            if db_project:
                db_project_statuses = session.exec(
                    select(ProjectStatus).where(ProjectStatus.project_id == project_id)
                ).all()
                
                for status in db_project_statuses:
                    session.delete(status)

                session.delete(db_project)
                session.commit()
                return True
            return False


__all__ = [ProjectService]
