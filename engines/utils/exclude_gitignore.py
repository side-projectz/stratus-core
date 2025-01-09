import logging
import fnmatch
from typing import List
from llama_index.core import Document

logger = logging.getLogger("uvicorn")


def exclude_gitignore_documents(documents: List[Document]):
    # for doc in documents:
    #     logger.debug(doc.metadata["file_path"])

    gitignore_doc = next(
        (doc for doc in documents if doc.metadata["file_name"] == ".gitignore"), None
    )

    logger.info(gitignore_doc)

    if not gitignore_doc:
        return documents

    gitignore_patterns = gitignore_doc.text.splitlines()
    logger.info(gitignore_patterns)

    filtered_documents = []
    for doc in documents:
        # Check if the document path matches any .gitignore pattern
        path = doc.metadata.get("path", "")
        if not any(fnmatch.fnmatch(path, pattern) for pattern in gitignore_patterns):
            filtered_documents.append(doc)

    return filtered_documents
