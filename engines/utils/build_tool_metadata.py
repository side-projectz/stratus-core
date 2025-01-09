import chromadb
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.core.indices import VectorStoreIndex


def build_tool_metadata(collection_name: str):

    chroma_client = chromadb.PersistentClient(path="storage/vector_store")
    collection = chroma_client.get_or_create_collection(collection_name)

    vector_store = ChromaVectorStore(
        chroma_collection=collection,
    )

    # Index this single document
    index = VectorStoreIndex.from_vector_store(vector_store=vector_store)
    query_engine = index.as_query_engine()

    PROMPT_NAME = (
        "Based on the structure and contents of this directory, suggest a concise and descriptive name "
        "that captures the purpose or main theme of the directory. Avoid generic terms and focus on clarity."
    )

    name_response = query_engine.query(PROMPT_NAME)
    tool_name = (
        name_response.response
        if hasattr(name_response, "response")
        else str(name_response)
    )

    PROMPT_DESCRIPTION = (
        "Provide a concise, high-level summary of this directory and its contents. "
        "Mention the files and subdirectories and their general purpose."
    )

    description_response = query_engine.query(PROMPT_DESCRIPTION)
    tool_description = (
        description_response.response
        if hasattr(description_response, "response")
        else str(description_response)
    )

    return tool_name, tool_description
