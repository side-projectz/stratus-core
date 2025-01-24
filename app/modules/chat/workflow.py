import dspy
from fastapi.exceptions import HTTPException
from llama_index.core import QueryBundle
from llama_index.core.postprocessor import SentenceTransformerRerank
from llama_index.core.response.pprint_utils import pprint_source_node
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

from app.config import LLM_MODEL, LLM_PROVIDER, LLM_PROVIDER_API_KEY
from app.modules.projects import ProjectService
from app.shared.chroma_db import ChromaDB


class RetrieverEvent(Event):
	query: str


class SemanticSearchEvent(Event):
	query: str


class ResponseGenerationEvent(Event):
	query: str
	nodes: list[NodeWithScore]


class RagWorkflow(Workflow):
	@step
	async def start_event(self, ctx: Context, e: StartEvent) -> RetrieverEvent:
		project_id = e.project_id
		project = ProjectService().get_project(id=project_id)
		if not project:
			raise HTTPException(status_code=404, detail="Project not found")

		lm = dspy.LM(
			model=f"{LLM_PROVIDER}/{LLM_MODEL}",
			api_key=LLM_PROVIDER_API_KEY,
		)

		await ctx.set("lm", lm)
		await ctx.set("collection_name", project.name)
		await ctx.set("query", e.query)

		return RetrieverEvent(query=e.query)

	@step
	async def retriever_event(
		self, ctx: Context, e: RetrieverEvent
	) -> SemanticSearchEvent:
		query = e.query
		collection_name = await ctx.get("collection_name")

		collection_index = ChromaDB(collection_name).as_vector_store_index()

		if collection_index is None:
			print("Index is empty, load some documents before querying!")
			return None

		retriever = VectorIndexRetriever(
			index=collection_index,
			similarity_top_k=10,
		)

		query_bundle = QueryBundle(query)
		retrieved_nodes = await retriever.aretrieve(query_bundle)

		print(f"Retrieved {len(retrieved_nodes)} nodes.")
		await ctx.set("retrieved_nodes", retrieved_nodes)
		await ctx.set("query_bundle", query_bundle)
		return SemanticSearchEvent(query=query)

	@step
	async def semantic_search(
		self, ctx: Context, e: SemanticSearchEvent
	) -> ResponseGenerationEvent:
		query = e.query
		query_bundle = await ctx.get("query_bundle")
		retrieved_nodes = await ctx.get("retrieved_nodes")

		reranker = SentenceTransformerRerank(
			model="cross-encoder/ms-marco-MiniLM-L-6-v2",
			top_n=10,
		)

		# reranker = LLMRerank(
		# 	llm=Settings.llm,
		# 	choice_batch_size=10,
		# 	top_n=5,
		# )

		# reranker = RankGPTRerank(
		# 	llm=Settings.llm,
		# 	top_n=5,
		# )

		retrieved_nodes = reranker.postprocess_nodes(retrieved_nodes, query_bundle)
		for node in retrieved_nodes:
			pprint_source_node(source_node=node)
			print("\n")

		return ResponseGenerationEvent(query=query, nodes=retrieved_nodes)

	@step
	async def generate_response(
		self, ctx: Context, e: ResponseGenerationEvent
	) -> StopEvent:
		query = await ctx.get("query")
		retrieved_nodes = e.nodes

		lm = await ctx.get("lm")
		dspy.configure(lm=lm)

		# rag = dspy.ChainOfThought("context, question -> response")
		rag = dspy.MIPROv2("context, question -> response")

		output = rag(
			context="\n".join([node.text for node in retrieved_nodes]),
			question=query,
		)

		res = {
			"response": output.response,
			"reasoning": output.reasoning,
		}

		return StopEvent(result=res["response"])
