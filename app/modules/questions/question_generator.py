from uuid import UUID

from fastapi import HTTPException
from pydantic import BaseModel, Field

from app.modules.projects import ProjectService
from app.shared.chroma_db import ChromaDB
from app.shared.llms import load_llm_model

from .schemas import QuestionsSchema


class QuestionList(BaseModel):
	questions: list[QuestionsSchema]


# async def generate_questions(project_id):
# 	"""
# 	Generate questions from the given text.
# 	"""
# 	project = ProjectService().get_project(id=project_id)
# 	if not project:
# 		raise HTTPException(status_code=404, detail="Project not found")

# 	reader = SimpleDirectoryReader(project.path)
# 	documents = reader.load_data()

# 	data_generator = DatasetGenerator.from_documents(documents)
# 	eval_questions = data_generator.generate_questions_from_nodes()

# 	llm = load_llm_model("openai")

# 	sllm = llm.as_structured_llm(output_cls=QuestionList)
# 	input_msg = ChatMessage.from_str(
# 		"Generate a set of 15 question, 5 questions for each levels 1-easy, 2-medium, and 3-hard for the given questions list."
# 	)
# 	input_msg_2 = ChatMessage.from_str(",".join(eval_questions))

# 	output = await sllm.achat([input_msg, input_msg_2])

# 	return output.raw


async def generate_questions(project_id, num: int = 1) -> QuestionList:
	project = ProjectService().get_project(id=project_id)
	if not project:
		raise HTTPException(status_code=404, detail="Project not found")
	collection_name = project.name
	collection_index = ChromaDB(collection_name).as_vector_store_index()
	query_engine = collection_index.as_query_engine(
		llm=load_llm_model("openai"),
		response_mode="tree_summarize",
		output_cls=QuestionList,
	)
	response = await query_engine.aquery(""" 
		Generate a question paper set with 15 question, \
        5 questions for each levels 1-easy, 2-medium, and 3-hard for the given questions list. \
		
		the generated qestions should be clear, concise and should contain the necessary information. \
		MUST be generated based on the features and functionalities of the system, \
		and NOT based on the just the text documents like README. \
    """)

	return response.response


async def generate_question(
	project_id, num: int = 1, level: str = "medium"
) -> QuestionList:
	project = ProjectService().get_project(id=project_id)
	if not project:
		raise HTTPException(status_code=404, detail="Project not found")
	collection_name = project.name
	collection_index = ChromaDB(collection_name).as_vector_store_index()
	query_engine = collection_index.as_query_engine(
		llm=load_llm_model("openai"),
		response_mode="tree_summarize",
		output_cls=QuestionList,
	)
	response = await query_engine.aquery(f""" 
		Your are an Expert in generating questions. \
		You are required to generate a question paper with {num} question of level {level}, \
		
		The questions - 
		will be answered by Middle School students. \
		should be detailed
		should contain the necessary information. \
		should not be confusing and should cleary state which feature or functionality of the system is being asked. \
		MUST be generated based on the features and functionalities of the system, \
		And NOT based on the just the text documents like README. \
    """)

	return response.response


class EvaluationResponse(BaseModel):
	score: float = Field(..., description="Score for the answer, 0-5")
	reasoning: str = Field(..., description="Reasoning for the score")
	ideal_answer: str = Field(..., description="Clear and concise Ideal answer")


async def evaluate_answer(project_id: str, question_str: str, answer_str: str):
	project = ProjectService().get_project(id=project_id)
	if not project:
		raise HTTPException(status_code=404, detail="Project not found")
	collection_name = project.name
	collection_index = ChromaDB(collection_name).as_vector_store_index()
	query_engine = collection_index.as_query_engine(
		llm=load_llm_model("openai"),
		response_mode="tree_summarize",
		output_cls=EvaluationResponse,
	)

	prompt = f"""
		Evaluate user's answer for the question
		[Question]: {question_str} 
		[Answer]: {answer_str}

		return the score and reasoning based on the answer
		the score should be between 0-5
		the reasoning should be a brief explanation why the score 
		the improvements should be a brief explanation on how the answer can be improved, if any 

	"""

	response = await query_engine.aquery(prompt)
	return response.response


async def rephrase_question(project_id: UUID, question_str: str) -> str:
	project = ProjectService().get_project(id=project_id)
	if not project:
		raise HTTPException(status_code=404, detail="Project not found")
	collection_name = project.name
	collection_index = ChromaDB(collection_name).as_vector_store_index()
	query_engine = collection_index.as_query_engine(
		llm=load_llm_model("openai"),
		response_mode="tree_summarize",
	)
	prompt = f"Rephrase the question in a simpler way:\n{question_str}"
	response = await query_engine.aquery(prompt)
	return response.response
