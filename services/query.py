import logging
from uuid import UUID
from models import SessionDep
from pydantic import BaseModel
from models.projects import Project
from fastapi import APIRouter, HTTPException
from engines.workflow.workflow import RagWorkflow

logger = logging.getLogger("uvicorn")

query_router = APIRouter(prefix="/query", tags=["Query"])


class QueryInput(BaseModel):
    query: str
    project_id: UUID


@query_router.post("/")
async def query(query_input: QueryInput, session: SessionDep):
    """
    Handles query requests by retrieving the project and associated collection
    and sending the query to the ChromaDB chat engine.
    """

    project = session.get(Project, query_input.project_id)
    logger.debug(project)

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    w = RagWorkflow(timeout=60, verbose=True)
    result = await w.run(project_id=project.id, query=query_input.query)
    print(str(result))
    return result


# try:
#     logger.info(query_input)

#     # Fetch the project using the project_id
#     project = session.get(Project, query_input.project_id)
#     logger.debug(project)

#     if not project:
#         raise HTTPException(status_code=404, detail="Project not found")

#     # Initialize the ChromaDB engine with the collection
#     chat_engine = ChromaDB(project.name).as_chat_engine()

#     # Send the query to ChromaDB
#     response = chat_engine.chat(message=query_input.query)
#     return {"response": response}

# except Exception as e:
#     logger.error(f"Error processing query: {e}")
#     raise HTTPException(status_code=500, detail="Internal Server Error")
