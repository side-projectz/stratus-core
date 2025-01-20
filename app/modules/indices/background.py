from app.modules.projects import (
	ProjectSchemas,
	ProjectStatusEnum,
	ProjectStatusSchema,
	ProjectStatusService,
)
from app.shared.chroma_db import ChromaDB
from app.utils import logger
from app.utils.git import is_git_repo

from .directory_loader import load_documents
from .ingestion_pipeline import build_ingestion_pipeline


class BackgroundIndexingArgs(ProjectSchemas.ProjectRead):
	status: ProjectStatusSchema.ProjectStatusRead


async def index_project_in_background(args: BackgroundIndexingArgs):
	try:
		logger.info("Background indexing task started")
		logger.info(args)

		project = BackgroundIndexingArgs(**args)
		project_status = project.status

		logger.debug(project)
		logger.debug(project_status)

		project_status_service = ProjectStatusService()

		project_status_service.update_project_status(
			project_status_id=project_status.id, status=ProjectStatusEnum.PROCESSING
		)
		is_git_repo(project.path)

		logger.debug(f"Dropping collection {project.name}")
		ChromaDB(project.name).drop_collection()

		logger.debug(f"Loading documents from {project.path}")
		all_documents = load_documents(path=project.path)
		logger.debug(f"Found {len(all_documents)} documents")

		pipeline = build_ingestion_pipeline(collection_name=project.name)
		await pipeline.arun(documents=all_documents, show_progress=True)

		project_status_service.update_project_status(
			project_status_id=project_status.id, status=ProjectStatusEnum.SUCCESS
		)
		logger.info("Background indexing task completed")

	except ValueError as e:
		logger.error(e)
		project_status_service.update_project_status(
			project_status_id=project_status.id, status=ProjectStatusEnum.FAILED
		)
		return
	except Exception as e:
		logger.error(e)
		project_status_service.update_project_status(
			project_status_id=project_status.id, status=ProjectStatusEnum.FAILED
		)
		return
