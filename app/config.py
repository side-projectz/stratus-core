import os

from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv())


# ======================= APPLICATION_CONFIGURATIONS ========================
# env = os.environ.items()
# print(env)


HOST = os.getenv("RAG_APP_HOST", "127.0.0.1")
PORT = int(os.getenv("RAG_APP_PORT", "8001"))

ENVIRONMENT = os.getenv("ENVIRONMENT", "prod")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")


ROOT_PATH = os.getcwd()

CHROMA_DB_PATH = "/database/vector_store"

# ======================= LLM_CONFIGURATIONS ========================
# LLM_PROVIDER = os.getenv("RAG_PROVIDER", "openai")
# LLM_MODEL = os.getenv("RAG_LLM_MODEL", "gpt-3.5-turbo")
# EMBEDDING_MODEL = os.getenv("RAG_EMBEDDING_MODEL", "text-embedding-3-small")

LLM_PROVIDER = "openai"
# LLM_MODEL = "gpt-3.5-turbo"
LLM_MODEL = "gpt-4o-mini"
EMBEDDING_MODEL = "text-embedding-3-small"

LLM_PROVIDER_BASE_URL = os.getenv("RAG_BASE_URL")
LLM_PROVIDER_API_KEY = os.getenv("RAG_API_KEY")

LLM_MAX_TOKENS = os.getenv("RAG_LLM_MAX_TOKENS")
LLM_TEMPERATURE = float(os.getenv("RAG_LLM_TEMPERATURE", 0.5))

CHUNK_SIZE = os.getenv("CHUNK_SIZE")
CHUNK_OVERLAP = os.getenv("CHUNK_OVERLAP")
