from llama_index.core.agent import ReActAgent

from engines.settings import init_settings
from engines.chroma_db import ChromaDB


def get_react_agent(collection_name: str):
    llm, _ = init_settings()
    collection = ChromaDB(collection_name)
    tool = collection.as_tool()
    agent = ReActAgent.from_tools(tools=[tool], llm=llm)
    return agent
