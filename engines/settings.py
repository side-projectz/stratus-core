import os
import logging
from llama_index.core import Settings
from llama_index.core.constants import DEFAULT_TEMPERATURE
from env_config import (
    LLM_PROVIDER,
    LLM_PROVIDER_BASE_URL,
    LLM_MODEL,
    EMBEDDING_MODEL,
    LLM_MAX_TOKENS,
    LLM_TEMPERATURE,
    LLM_PROVIDER_API_KEY,
    CHUNK_OVERLAP,
    CHUNK_SIZE,
)
from llama_index.llms.openai import OpenAI
from llama_index.llms.openai.base import DEFAULT_OPENAI_MODEL
from llama_index.embeddings.openai import OpenAIEmbedding

from llama_index.llms.ollama import Ollama
from llama_index.llms.ollama.base import DEFAULT_CONTEXT_WINDOW, DEFAULT_REQUEST_TIMEOUT
from llama_index.embeddings.ollama import OllamaEmbedding


logger = logging.getLogger("uvicorn")


def init_settings():
    logger.info(LLM_PROVIDER)
    logger.debug(f"LLM: {LLM_MODEL}")
    logger.debug(f"Embed_model: {EMBEDDING_MODEL}")

    match LLM_PROVIDER:
        case "openai":
            logger.info("Loading OpenAI models")
            llm, embed_model = init_openai()
        case "ollama":
            logger.info("Loading Ollama models")
            llm, embed_model = init_ollama()
        case _:
            raise ValueError(f"Invalid model provider: {LLM_PROVIDER}")

    Settings.chunk_size = int(CHUNK_SIZE or "1024")
    Settings.chunk_overlap = int(CHUNK_OVERLAP or "20")

    return llm, embed_model


def init_ollama():

    BASE_URL = LLM_PROVIDER_BASE_URL or "http://127.0.0.1:11434"

    REQUEST_TIMEOUT = float(
        os.getenv("OLLAMA_REQUEST_TIMEOUT", DEFAULT_REQUEST_TIMEOUT)
    )

    embed_model = OllamaEmbedding(base_url=BASE_URL, model_name=EMBEDDING_MODEL)
    llm_model = Ollama(
        base_url=BASE_URL,
        model=LLM_MODEL,
        context_window=DEFAULT_CONTEXT_WINDOW,
        temperature=LLM_TEMPERATURE or DEFAULT_TEMPERATURE,
        request_timeout=REQUEST_TIMEOUT,
    )

    Settings.llm = llm_model
    Settings.embed_model = embed_model

    return llm_model, embed_model


def init_openai():
    REQUEST_TIMEOUT = float(
        os.getenv("OLLAMA_REQUEST_TIMEOUT", DEFAULT_REQUEST_TIMEOUT)
    )

    embed_model = OpenAIEmbedding(
        api_key=LLM_PROVIDER_API_KEY, model_name=EMBEDDING_MODEL
    )
    llm_model = OpenAI(
        api_key=LLM_PROVIDER_API_KEY,
        model=LLM_MODEL or DEFAULT_OPENAI_MODEL,
        context_window=DEFAULT_CONTEXT_WINDOW,
        request_timeout=REQUEST_TIMEOUT,
        temperature=float(LLM_TEMPERATURE or DEFAULT_TEMPERATURE),
        max_tokens=int(LLM_MAX_TOKENS or "1024"),
    )

    Settings.llm = llm_model
    Settings.embed_model = embed_model

    return llm_model, embed_model
