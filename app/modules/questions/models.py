from datetime import datetime
from uuid import UUID

from sqlmodel import Field, SQLModel

from app.utils import generate_timestamp, generate_uuid


class QuestionBase(SQLModel):
	question: str = Field(
		min_length=1, max_length=500, description="The question to be asked"
	)
	level: int = Field(
		description="The level of the question eg, easy, medium, hard represented as (1, 2, 3)"
	)


class Question(QuestionBase, table=True):
	id: UUID = Field(default_factory=generate_uuid, primary_key=True)
	project_id: UUID = Field(
		foreign_key="project.id",
		description="The project id to which the question belongs",
	)

	created_at: datetime = Field(default_factory=generate_timestamp)
	updated_at: datetime = Field(default_factory=generate_timestamp)


class AnswerBase(SQLModel):
	answer: str = Field(
		min_length=1, max_length=500, description="The answer to the question"
	)
	question_id: UUID = Field(
		index=True,
		foreign_key="question.id",
		description="The question id to which the answer belongs",
	)
	score: float = Field(description="Score for the answer, 0-5")
	reasoning: str = Field(description="Reasoning for the score")
	ideal_answer: str = Field(description="Ideal answer")


class Answer(AnswerBase, table=True):
	id: UUID = Field(default_factory=generate_uuid, primary_key=True)
	project_id: UUID = Field(
		index=True,
		foreign_key="project.id",
		description="The project id to which the answer belongs",
	)

	created_at: datetime = Field(default_factory=generate_timestamp)
	updated_at: datetime = Field(default_factory=generate_timestamp)


__all__ = [Question, QuestionBase, Answer, AnswerBase]
