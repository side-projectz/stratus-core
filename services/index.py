import logging
from uuid import UUID
from fastapi import APIRouter, HTTPException, BackgroundTasks
from sqlmodel import select
from pydantic import BaseModel

from models import SessionDep

from engines.pipelines.ingestion import build_ingestion_pipeline
from engines.loaders.directory import load_documents
from engines.utils.exclude_gitignore import exclude_gitignore_documents


from models.projects import Project, get_project

from models.project_status import (
    ProjectStatus,
    ProjectStatusEnum,
    update_project_status,
)


logger = logging.getLogger("uvicorn")

index_router = APIRouter(prefix="/index", tags=["Index"])


async def index_project_in_background(project_status_db: ProjectStatus):
    try:
        logger.info("start indexing")
        update_project_status(project_status_db.id, ProjectStatusEnum.PROCESSING)

        project = get_project(project_status_db.project_id)
        logger.info(project)

        collection_name = project.name
        documents = load_documents(project=project)
        logger.info(f"Found {len(documents)} documents")

        documents = exclude_gitignore_documents(documents)
        logger.info(f"Found {len(documents)} documents after excluding")

        pipeline = build_ingestion_pipeline(collection_name)
        await pipeline.arun(documents=documents, show_progress=True)

        logger.info("Indexing Success")
        project_status_db.status = ProjectStatusEnum.SUCCESS

        logger.info("Pipeline run completed")
        update_project_status(project_status_db.id, ProjectStatusEnum.SUCCESS)
    except Exception as e:
        logger.info("Indexing Failed")
        logger.debug(e)
        project_status_db.status = ProjectStatusEnum.FAILED
        update_project_status(project_status_db.id, ProjectStatusEnum.FAILED)

    return project_status_db


class NewIndexBody(BaseModel):
    project_id: UUID


@index_router.post("/")
async def start_indexing(
    index_project: NewIndexBody, session: SessionDep, background_tasks: BackgroundTasks
):
    print(index_project)

    project = get_project(index_project.project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    project_status = ProjectStatus(
        project_id=project.id, status=ProjectStatusEnum.QUEUE
    )
    session.add(project_status)
    session.commit()
    session.refresh(project_status)

    background_tasks.add_task(index_project_in_background, project_status)
    return {"status": True, "message": "Indexing has started"}


@index_router.get("/status")
def index_status(project_id: UUID, session: SessionDep):
    project = session.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    project_status = session.exec(
        select(ProjectStatus)
        .where(ProjectStatus.project_id == project.id)
        .order_by(ProjectStatus.created_at.desc())
    ).first()

    if not project_status:
        raise HTTPException(status_code=404, detail="Project status not found")

    return project_status
