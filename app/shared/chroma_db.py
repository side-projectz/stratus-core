import chromadb
from chromadb.config import Settings as ChromaDbSettings
from llama_index.core.indices import VectorStoreIndex
from llama_index.vector_stores.chroma import ChromaVectorStore

from app.config import (
	CHROMA_DB_PATH,
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
		return self.client.get_or_create_collection(
			self.collection_name,
		)

	def drop_collection(self):
		collection = self.get_collection()
		if collection:
			self.client.delete_collection(self.collection_name)

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
