from llama_index.core.ingestion import IngestionPipeline

from app.shared.chroma_db import ChromaDB
from app.shared.embed_models import load_embedding_model
from app.utils import logger


def build_ingestion_pipeline(collection_name: str):
	try:
		embedding_model = load_embedding_model()
		chroma_collection = ChromaDB(collection_name)
		vector_store = chroma_collection.as_vector_store()

		transformations = [
			embedding_model,
		]

		pipeline = IngestionPipeline(
			transformations=transformations,
			vector_store=vector_store,
			project_name=collection_name,
			disable_cache=True,
		)

		return pipeline
	except Exception as e:
		logger.error(e)
		raise e
