from pydantic import BaseModel
from uuid import UUID


class ProjectStatusSchema:
    class ProjectStatusCreate(BaseModel):
        project_id: UUID
        status: str

    class ProjectStatusRead(BaseModel):
        id: UUID
        project_id: UUID
        status: str

    class ProjectStatusUpdate(BaseModel):
        id: UUID
        status: str
    
    class ProjectStatusList(BaseModel):
        project_statuses: list["ProjectStatusSchema.ProjectStatusRead"] = []


__all__ =[ProjectStatusSchema]