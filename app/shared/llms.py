import os

from llama_index.core.constants import DEFAULT_TEMPERATURE
from llama_index.llms.ollama import Ollama
from llama_index.llms.openai import OpenAI

from app.config import (
	LLM_MAX_TOKENS,
	LLM_MODEL,
	LLM_PROVIDER,
	LLM_PROVIDER_API_KEY,
	LLM_PROVIDER_BASE_URL,
	LLM_TEMPERATURE,
)
from app.utils import logger


def load_llm_model(_provider: str | None):
	provider = _provider or LLM_PROVIDER

	logger.info(provider)
	logger.debug(f"LLM_MODEL: {LLM_MODEL}")

	try:
		match LLM_PROVIDER:
			case "openai":
				model = init_openai_llm()
			case "ollama":
				model = init_ollama_llm()
			case _:
				raise ValueError(f"Invalid model provider: {LLM_PROVIDER}")
		return model
	except Exception as e:
		logger.error(e)
		raise e


def init_openai_llm():
	from llama_index.core.constants import DEFAULT_CONTEXT_WINDOW

	llm_model = OpenAI(
		api_key=LLM_PROVIDER_API_KEY,
		model=LLM_MODEL or "gpt-4o-mini",
		context_window=DEFAULT_CONTEXT_WINDOW,
		temperature=float(LLM_TEMPERATURE or DEFAULT_TEMPERATURE),
		max_tokens=int(LLM_MAX_TOKENS or "1024"),
	)

	return llm_model


def init_ollama_llm():
	from llama_index.llms.ollama.base import (
		DEFAULT_CONTEXT_WINDOW,
		DEFAULT_REQUEST_TIMEOUT,
	)

	BASE_URL = LLM_PROVIDER_BASE_URL or "http://127.0.0.1:11434"
	REQUEST_TIMEOUT = float(
		os.getenv("OLLAMA_REQUEST_TIMEOUT", DEFAULT_REQUEST_TIMEOUT)
	)

	llm_model = Ollama(
		base_url=BASE_URL,
		model=LLM_MODEL,
		context_window=DEFAULT_CONTEXT_WINDOW,
		temperature=LLM_TEMPERATURE or DEFAULT_TEMPERATURE,
		request_timeout=REQUEST_TIMEOUT,
	)

	return llm_model
