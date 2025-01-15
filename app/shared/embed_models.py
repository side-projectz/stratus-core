from llama_index.embeddings.ollama import OllamaEmbedding
from llama_index.embeddings.openai import OpenAIEmbedding

from app.config import (
	EMBEDDING_MODEL,
	LLM_PROVIDER,
	LLM_PROVIDER_API_KEY,
	LLM_PROVIDER_BASE_URL,
)
from app.utils import logger


def load_embedding_model(provider: str | None = None):
	_provider = provider or LLM_PROVIDER

	logger.info(_provider)
	logger.debug(f"Embed_model: {EMBEDDING_MODEL}")

	try:
		match _provider:
			case "openai":
				model = init_openai_embed()
			case "ollama":
				model = init_ollama_embed()
			case _:
				raise ValueError(f"Invalid model provider: {LLM_PROVIDER}")
		return model
	except Exception as e:
		logger.error(e)
		raise e


def init_openai_embed():
	embed_model = OpenAIEmbedding(
		api_key=LLM_PROVIDER_API_KEY, model_name=EMBEDDING_MODEL
	)

	return embed_model


def init_ollama_embed():
	BASE_URL = LLM_PROVIDER_BASE_URL or "http://127.0.0.1:11434"

	embed_model = OllamaEmbedding(
		base_url=BASE_URL,
		model_name=EMBEDDING_MODEL,
		# embed_batch_size=50,
	)

	return embed_model
