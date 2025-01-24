from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy.sql import exists
from sqlmodel import select

from app.database import Session, engine
from app.modules.projects import ProjectService

from .models import Answer, AnswerBase, Question, QuestionBase
from .question_generator import evaluate_answer, generate_question, rephrase_question

project_service = ProjectService()


class QuestionService:
	def __init__(self):
		pass

	def un_answered_questions(self, project_id: UUID):
		with Session(engine) as session:
			unanswered_questions = session.exec(
				select(Question)
				.where(
					Question.project_id == project_id,
					~exists().where(Answer.question_id == Question.id),
				)
				.order_by(Question.created_at.desc())
				.limit(10)
			).all()
			if not unanswered_questions:
				raise ValueError("Questions not found.")
		return unanswered_questions

	def retrieve_question(self, question_id: UUID):
		with Session(engine) as session:
			question = session.exec(
				select(Question).where(Question.id == question_id)
			).first()
			if not question:
				raise ValueError("Question not found.")

		return question

	def create_question(self, project_id: UUID, question_data: QuestionBase):
		with Session(engine) as session:
			question_data = Question(
				**question_data.model_dump(), project_id=project_id
			)
			session.add(question_data)
			session.commit()
			session.refresh(question_data)
		return question_data

	def retrieve_answer(self, question_id: UUID):
		with Session(engine) as session:
			answer = session.exec(
				select(Answer).where(Answer.question_id == question_id)
			).first()
			if not answer:
				raise ValueError("Answer not found.")

		return answer

	def create_answer(self, project_id: UUID, answer_data: AnswerBase):
		with Session(engine) as session:
			answer_data = Answer(**answer_data.model_dump(), project_id=project_id)
			session.add(answer_data)
			session.commit()
			session.refresh(answer_data)
		return answer_data

	async def generate(self, project_id: UUID):
		try:
			questions_list = self.un_answered_questions(project_id)
		except ValueError:
			questions_list = None

		if questions_list:
			return {"questions": questions_list}

		questions_list = await generate_question(project_id=project_id, num=5)

		with Session(engine) as session:
			for question in questions_list.questions:
				question_data = Question(**question.model_dump(), project_id=project_id)
				session.add(question_data)
				session.commit()
				session.refresh(question_data)

		return questions_list

	async def evaluate(self, project_id: UUID, question_id: UUID, answer: str):
		project_obj = project_service.get_project(id=project_id)
		question_obj = self.retrieve_question(question_id=question_id)

		evaluated = await evaluate_answer(
			project_id=project_obj.id,
			question_str=question_obj.question,
			answer_str=answer,
		)

		try:
			answer_obj = self.retrieve_answer(question_id=question_obj.id)
		except ValueError:
			answer_obj = None

		with Session(engine) as session:
			if answer_obj:
				answer_obj.score = evaluated.score
				answer_obj.reasoning = evaluated.reasoning
				answer_obj.ideal_answer = evaluated.ideal_answer
				answer_obj.updated_at = datetime.now(timezone.utc)
				session.add(answer_obj)
				session.commit()
				session.refresh(answer_obj)
			else:
				answer_obj = Answer(
					answer=answer,
					score=evaluated.score,
					reasoning=evaluated.reasoning,
					question_id=question_id,
					project_id=project_id,
					ideal_answer=evaluated.ideal_answer,
				)
				session.add(answer_obj)
				session.commit()
				session.refresh(answer_obj)

		return answer_obj

	async def rephrase(self, project_id: UUID, question_id: UUID, question_list: str):
		question_obj = self.retrieve_question(question_id)
		rephrased = await rephrase_question(
			project_id=project_id, question_str=question_list
		)
		with Session(engine) as session:
			question = Question(
				question=str(rephrased),
				level=question_obj.level,
				project_id=project_id,
			)
			session.add(question)
			session.commit()
			session.refresh(question)
		return question
