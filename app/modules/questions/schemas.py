from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class QuestionsSchema(BaseModel):
	id: UUID = Field(default_factory=uuid4)
	question: str = Field(..., description="The question to be asked")
	level: int = Field(
		..., description="The level of the question eg, easy, medium, hard"
	)
