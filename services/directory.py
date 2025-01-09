from typing import List, Annotated
from fastapi import APIRouter, Query, HTTPException
from sqlmodel import select
from uuid import UUID

from models.projects import ProjectCreate
from models import SessionDep
from models.projects import Project, ProjectPublic
from models.project_status import ProjectStatus, ProjectStatusEnum

directory_router = APIRouter(prefix="/project", tags=["Project"])


@directory_router.get("/", response_model=List[ProjectPublic])
def get_project_list(
    session: SessionDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
):
    projects = session.exec(select(Project).offset(offset).limit(limit)).all()
    return projects


@directory_router.post("/")
def add_project(new_project: ProjectCreate, session: SessionDep):
    project = Project(**new_project.model_dump())

    exist = session.exec(select(Project).where(Project.path == project.path)).first()
    if exist:
        raise HTTPException(status_code=409, detail="Project already exists")

    session.add(project)
    session.commit()
    session.refresh(project)

    project_status = ProjectStatus(
        project_id=project.id, status=ProjectStatusEnum.QUEUE
    )
    session.add(project_status)
    session.commit()
    session.refresh(project_status)
    
    return project


@directory_router.delete("/{project_id}")
def delete_project(project_id: UUID, session: SessionDep):
    project = session.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    session.delete(project)
    session.commit()
    return {"status": True}
