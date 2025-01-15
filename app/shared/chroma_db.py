import chromadb
from chromadb.config import Settings as ChromaDbSettings
from chromadb.utils.embedding_functions.ollama_embedding_function import (
	OllamaEmbeddingFunction,
)
from chromadb.utils.embedding_functions.openai_embedding_function import (
	OpenAIEmbeddingFunction,
)
from llama_index.core.indices import VectorStoreIndex
from llama_index.vector_stores.chroma import ChromaVectorStore

from app.config import (
	CHROMA_DB_PATH,
	EMBEDDING_MODEL,
	LLM_PROVIDER,
	LLM_PROVIDER_API_KEY,
	LLM_PROVIDER_BASE_URL,
	ROOT_PATH,
)


class ChromaDB:
	def __init__(self, name: str, allow_reset: bool = False):
		allow_reset_str = "True" if allow_reset else "False"
		self.collection_name = name
		path = ROOT_PATH + CHROMA_DB_PATH
		self.client = chromadb.PersistentClient(
			path=path, settings=ChromaDbSettings(allow_reset=allow_reset_str)
		)

	def get_collection(self):
		# embedding_fn = _load_chroma_embedding_function()
		return self.client.get_or_create_collection(
			self.collection_name,
			# embedding_function=embedding_fn
		)

	def as_vector_store(self):
		chroma_collection = self.get_collection()
		vector_store = ChromaVectorStore(
			chroma_collection=chroma_collection,
		)
		return vector_store

	def as_vector_store_index(self):
		vector_store = self.as_vector_store()
		index = VectorStoreIndex.from_vector_store(vector_store=vector_store)
		return index

	def as_query_engine(self):
		index = self.as_vector_store_index()
		return index.as_query_engine()

	def as_chat_engine(self):
		index = self.as_vector_store_index()
		return index.as_chat_engine()


def _load_chroma_embedding_function(provider: str | None = None):
	_provider = provider or LLM_PROVIDER

	match _provider:
		case "openai":
			embedding_fn = OpenAIEmbeddingFunction(
				api_key=LLM_PROVIDER_API_KEY, model_name=EMBEDDING_MODEL
			)
		case "ollama":
			embedding_fn = OllamaEmbeddingFunction(
				model_name=EMBEDDING_MODEL,
				url=LLM_PROVIDER_BASE_URL + "/api/embeddings",
			)
		case _:
			raise ValueError(f"Invalid model provider: {LLM_PROVIDER}")

	return embedding_fn
