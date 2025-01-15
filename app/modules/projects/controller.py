from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query

from app.utils import logger

from .schemas import ProjectSchemas
from .service import ProjectService
from .status import ProjectStatusSchema, ProjectStatusService

project_router = APIRouter(prefix="/project", tags=["Project"])
project_service = ProjectService()
project_status_service = ProjectStatusService()


@project_router.get("/", response_model=ProjectSchemas.ProjectList)
def get_project_list(
	offset: int = 0,
	limit: Annotated[int, Query(le=100)] = 100,
):
	logger.debug(f"Getting project list with offset={offset} and limit={limit}")
	return project_service.get_project_list(offset=offset, limit=limit)


@project_router.get("/{project_id}", response_model=ProjectSchemas.ProjectDetails)
def get_project(project_id: str):
	try:
		logger.debug(f"Getting project with id={project_id}")
		return project_service.get_project(id=UUID(project_id))
	except ValueError as e:
		raise HTTPException(status_code=404, detail=str(e))


@project_router.post("/", response_model=ProjectSchemas.ProjectRead)
def create_project(new_project: ProjectSchemas.ProjectCreate):
	try:
		return project_service.create_project(project_data=new_project)
	except ValueError as e:
		raise HTTPException(status_code=400, detail=str(e))


@project_router.put("/{project_id}", response_model=ProjectSchemas.ProjectRead)
def update_project(project_id: str, project_data: ProjectSchemas.ProjectUpdate):
	try:
		return project_service.update_project(
			project_id=UUID(project_id), project_data=project_data
		)
	except ValueError as e:
		raise HTTPException(status_code=404, detail=str(e))


@project_router.delete("/{project_id}")
def delete_project(project_id: str):
	return project_service.delete_project(project_id=UUID(project_id))


# Project Status Router
@project_router.get(
	"/{project_id}/status", response_model=ProjectStatusSchema.ProjectStatusRead
)
def get_project_status(project_id: str):
	try:
		return project_status_service.get_project_status_by_project_id(
			project_id=UUID(project_id)
		)
	except ValueError as e:
		raise HTTPException(status_code=404, detail=str(e))
