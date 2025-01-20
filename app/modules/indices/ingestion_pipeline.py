from llama_index.core.ingestion import DocstoreStrategy, IngestionPipeline
from llama_index.core.storage.docstore import SimpleDocumentStore

# from llama_index.core.storage.chat_store import SimpleChatStore
# from llama_index.core.storage.index_store import SimpleIndexStore
# from llama_index.core.storage.storage_context import StorageContext, DEFAULT_PERSIST_DIR
from app.shared.chroma_db import ChromaDB
from app.shared.embed_models import load_embedding_model
from app.utils import logger


def build_ingestion_pipeline(collection_name: str):
	try:
		embedding_model = load_embedding_model()
		chroma_collection = ChromaDB(collection_name)
		vector_store = chroma_collection.as_vector_store()

		doc_store = SimpleDocumentStore.from_persist_dir(
			persist_dir="database/docstore",
		)

		transformations = [
			embedding_model,
		]

		pipeline = IngestionPipeline(
			transformations=transformations,
			vector_store=vector_store,
			docstore=doc_store,
			docstore_strategy=DocstoreStrategy.UPSERTS_AND_DELETE,
			project_name=collection_name,
			disable_cache=True,
		)

		return pipeline
	except Exception as e:
		logger.error(e)
		raise e
