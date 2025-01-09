import os
from dotenv import load_dotenv


load_dotenv()

# ======================= APPLICATION_CONFIGURATIONS ========================
ROOT_PATH = os.getcwd()

CHROMA_DB_PATH = "/database/vector_store"

# ======================= LLM_CONFIGURATIONS ========================
LLM_PROVIDER = os.getenv("RAG_PROVIDER", "openai")

LLM_MODEL = os.getenv("RAG_LLM_MODEL", "gpt-3.5-turbo")
EMBEDDING_MODEL = os.getenv("RAG_EMBEDDING_MODEL", "text-embedding-3-small")

LLM_PROVIDER_BASE_URL = os.getenv("RAG_BASE_URL")
LLM_PROVIDER_API_KEY = os.getenv("RAG_API_KEY")

LLM_MAX_TOKENS = os.getenv("RAG_LLM_MAX_TOKENS")
LLM_TEMPERATURE = os.getenv("RAG_LLM_TEMPERATURE")

CHUNK_SIZE = os.getenv("CHUNK_SIZE", "1024")
CHUNK_OVERLAP = os.getenv("CHUNK_OVERLAP", "20")
