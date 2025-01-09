import re
import os
from typing import List, Dict
from llama_index.core import Document


def exclude_documents(
    documents: List[Document], excludes: Dict[str, List[str]]
) -> List[Document]:
    """
    Filter out documents based on the given exclusion criteria.

    excludes is a dict that may contain:
      - "regex": list of regex patterns to match against the full file path.
      - "file_ext": list of file extensions (e.g. [".png", ".jpg"]).
      - "dir": list of directory names that, if present in the path, exclude the file.
      - "file": list of exact file paths (relative to the base directory) to exclude.

    The file path is something like "some/dir/file.txt".
    The "file" exclusion means if there's an exact match of the file path, it gets excluded.
    """

    regex_patterns = excludes.get("regex", [])
    file_extensions = excludes.get("ext", [])
    excluded_dirs = excludes.get("dir", [])
    excluded_files = excludes.get("file", [])

    # Normalize excluded_files by stripping leading/trailing slashes
    excluded_files = [f.strip("/") for f in excluded_files]

    def matches_exclude(file_path: str) -> bool:
        normalized_path = file_path.strip("/")
        parts = normalized_path.split("/") if normalized_path else []

        filename = parts[-1] if parts else ""
        directories = parts[:-1] if len(parts) > 1 else []

        # 1. Check exact file matches
        # If normalized_path is exactly in excluded_files, exclude it
        if normalized_path in excluded_files:
            return True

        # 2. Check regex patterns
        for pattern in regex_patterns:
            if re.search(pattern, file_path):
                return True

        # 3. Check file extensions
        _, ext = os.path.splitext(filename)
        if ext.lower() in (e.lower() for e in file_extensions):
            return True

        # 4. Check directories
        for d in directories:
            if d in excluded_dirs:
                return True

        return False

    filtered_docs = []
    for doc in documents:
        file_path = doc.metadata.get("file_path", "unknown")
        if not matches_exclude(file_path):
            filtered_docs.append(doc)

    return filtered_docs
