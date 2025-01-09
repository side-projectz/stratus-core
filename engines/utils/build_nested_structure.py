from typing import List, Dict, Any
from collections import defaultdict
from llama_index.core import Document

def build_nested_structure(documents: List[Document]) -> Dict[str, Any]:
    """
    Build a nested dictionary representing the folder/file hierarchy.
    """
    root = defaultdict(dict)
    for doc in documents:
        file_path = doc.metadata.get("file_path", "unknown")
        parts = file_path.strip("/").split("/")
        current = root
        for part in parts[:-1]:
            current = current.setdefault(part, {})
        current[parts[-1]] = doc
    return root
