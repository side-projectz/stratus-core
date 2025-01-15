from uuid import UUID

from fastapi import APIRouter, BackgroundTasks
from pydantic import BaseModel

from app.modules.projects import ProjectService, ProjectStatusEnum, ProjectStatusService
from app.utils import logger

from .background import index_project_in_background

indices_router = APIRouter(prefix="/index", tags=["Index"])


class IndexProjectBody(BaseModel):
	project_id: UUID


@indices_router.post("/")
async def index_project(
	data: IndexProjectBody,
	background_tasks: BackgroundTasks,
):
	try:
		logger.debug(f"Indexing project {data.project_id}")
		project = ProjectService().get_project(id=data.project_id)
		if not project:
			return {"message": "Project not found."}
		project_status_service = ProjectStatusService()
		project_status = project_status_service.create_project_status(
			project_id=data.project_id, status=ProjectStatusEnum.QUEUE
		)

		if project_status and project_status.status == ProjectStatusEnum.PROCESSING:
			return {"message": "Project is already being indexed."}

		if project_status and project_status.status == ProjectStatusEnum.SUCCESS:
			return {"message": "Project has already been indexed."}

		if project_status and project_status.status == ProjectStatusEnum.FAILED:
			return {"message": "Project indexing failed."}

		args = {
			"id": project.id,
			"name": project.name,
			"path": project.path,
			"status": project_status,
		}

		background_tasks.add_task(index_project_in_background, args)
		return {"message": "Project indexing started"}

	except Exception as e:
		logger.error(e)
		return {"message": "Failed to index project."}

		# project_status = ProjectStatusService().get_project_status_by_project_id(
		#     project_id=data.project_id
		# )

		# if project_status and project_status.status == ProjectStatusEnum.PROCESSING:
		#     return {"message": "Project is already being indexed."}

		# if project_status and project_status.status == ProjectStatusEnum.SUCCESS:
		#     return {"message": "Project has already been indexed."}

		# if project_status and project_status.status == ProjectStatusEnum.FAILED:
		#     return {"message": "Project indexing failed."}
