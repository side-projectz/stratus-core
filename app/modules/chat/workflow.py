from fastapi.exceptions import HTTPException
from llama_index.core import QueryBundle, Settings
from llama_index.core.postprocessor import SentenceTransformerRerank
from llama_index.core.response.pprint_utils import pprint_source_node
from llama_index.core.response_synthesizers import CompactAndRefine
from llama_index.core.retrievers import VectorIndexRetriever
from llama_index.core.schema import NodeWithScore
from llama_index.core.workflow import (
	Context,
	Event,
	StartEvent,
	StopEvent,
	Workflow,
	step,
)

from app.modules.projects import ProjectService
from app.shared.chroma_db import ChromaDB


class SemanticSearchEvent(Event):
	query: str
	collection_name: str


class ResponseGenerationEvent(Event):
	query: str
	nodes: list[NodeWithScore]


class RagWorkflow(Workflow):
	@step
	async def start_event(self, ctx: Context, e: StartEvent) -> SemanticSearchEvent:
		project_id = e.project_id
		project = ProjectService().get_project(id=project_id)
		if not project:
			raise HTTPException(status_code=404, detail="Project not found")

		return SemanticSearchEvent(query=e.query, collection_name=project.name)

	@step
	async def semantic_search(
		self, ctx: Context, e: SemanticSearchEvent
	) -> ResponseGenerationEvent:
		collection_name = e.collection_name
		query = e.query

		collection_index = ChromaDB(collection_name).as_vector_store_index()
		query_bundle = QueryBundle(query)
		retriever = VectorIndexRetriever(
			index=collection_index,
			similarity_top_k=10,
		)
		retrieved_nodes = retriever.retrieve(query_bundle)
		reranker = SentenceTransformerRerank(
			model="cross-encoder/ms-marco-MiniLM-L-6-v2",
			top_n=5,
		)
		retrieved_nodes = reranker.postprocess_nodes(retrieved_nodes, query_bundle)
		for node in retrieved_nodes:
			pprint_source_node(source_node=node)

		return ResponseGenerationEvent(query=query, nodes=retrieved_nodes)

	@step
	async def generate_response(
		self, ctx: Context, e: ResponseGenerationEvent
	) -> StopEvent:
		query = e.query
		retrieved_nodes = e.nodes
		llm = Settings.llm

		summarizer = CompactAndRefine(llm=llm, streaming=False, verbose=True)
		response = await summarizer.asynthesize(query, nodes=retrieved_nodes)

		return StopEvent(result=str(response))
