from uuid import UUID

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.modules.projects import ProjectService, ProjectStatusEnum
from app.utils import logger

from .workflow import RagWorkflow

chat_router = APIRouter(prefix="/chat", tags=["Chat"])


class QueryInput(BaseModel):
	query: str
	project_id: UUID


@chat_router.post("/")
async def chat(query_input: QueryInput):
	"""
	Handles chat requests by sending the query to the ChromaDB chat engine.
	"""
	logger.debug(query_input)
	try:
		project = ProjectService().get_project(id=query_input.project_id)

		if not project:
			raise HTTPException(status_code=404, detail="Project not found")

		if project.status and project.status == ProjectStatusEnum.PROCESSING:
			raise HTTPException(
				detail="Project is processing",
				status_code=400,
			)

		if not project.status or project.status != ProjectStatusEnum.SUCCESS:
			raise HTTPException(
				detail="Project not ready",
				status_code=400,
			)

		w = RagWorkflow(timeout=60, verbose=True)
		result = await w.run(project_id=query_input.project_id, query=query_input.query)
		print(str(result))
		return result

	except Exception as e:
		logger.error(e)
		raise HTTPException(status_code=501, detail="Not implemented")
