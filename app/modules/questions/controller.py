from uuid import UUID

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.modules.projects import ProjectService

from .service import QuestionService

router = APIRouter(
	tags=["Questions"],
)

project_service = ProjectService()
question_service = QuestionService()


class GenerateQuestionsBody(BaseModel):
	project_id: UUID


@router.post("/generate")
async def question_generate(body: GenerateQuestionsBody):
	try:
		project = project_service.get_project(id=body.project_id)
		if not project:
			raise HTTPException(status_code=404, detail="Project not found")
		questions = await question_service.generate(project_id=project.id)
		return questions
	except ValueError as e:
		raise HTTPException(status_code=400, detail=str(e))


class EvaluateAnswerBody(BaseModel):
	project_id: UUID
	question_id: UUID
	answer: str


@router.post("/evaluate")
async def answer_evaluate(body: EvaluateAnswerBody):
	try:
		project = project_service.get_project(id=body.project_id)
		if not project:
			raise HTTPException(status_code=404, detail="Project not found")

		result = await question_service.evaluate(
			project_id=project.id,
			question_id=body.question_id,
			answer=body.answer,
		)
		return result
	except ValueError as e:
		raise HTTPException(status_code=400, detail=str(e))


class RephraseQuestionBody(BaseModel):
	project_id: UUID
	question_id: UUID
	question_list: str


@router.post("/rephrase")
async def question_rephrase(body: RephraseQuestionBody):
	try:
		rephrased = await question_service.rephrase(
			project_id=body.project_id,
			question_id=body.question_id,
			question_list=body.question_list,
		)
		return rephrased
	except ValueError as e:
		raise HTTPException(status_code=400, detail=str(e))
