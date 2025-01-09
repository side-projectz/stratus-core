import logging
from models.projects import Project


logger = logging.getLogger("uvicorn")


def load_documents(project: Project):
    from llama_index.core.readers import SimpleDirectoryReader

    try:
        import nest_asyncio

        nest_asyncio.apply()
        loader = SimpleDirectoryReader(
            recursive=True,
            filename_as_id=True,
            raise_on_error=True,
            input_dir=project.path,
            exclude_hidden=True,
            exclude=[
                "*.crx",
                "*.pem",
                "*.zip",
                "*.yaml",
                "*.png",
                "*.jpg",
                "*.jpeg",
                "*.gif",
                "*.pdf",
                "*.docx",
                "*.pptx",
                "*.xlsx",
                "*.mp4",
                "*.avi",
                "*.mov",
                "*.mp3",
                "*.wav",
                "*.map",
                "*.js",
                "*.css",
                "*.json",
                "*.lock",
            ],
        )
        documents = loader.load_data()
        for doc in documents:
            content = doc.text
            metadata = f"""
Name: {doc.metadata['file_name']}            
Path: {doc.metadata['file_path']} \n
"""
            doc.set_content(metadata + content)
        
        return documents

    except Exception as e:
        import sys
        import traceback

        # Catch the error if the data dir is empty
        # and return as empty document list
        _, _, exc_traceback = sys.exc_info()
        function_name = traceback.extract_tb(exc_traceback)[-1].name
        if function_name == "_add_files":
            logger.warning(
                f"Failed to load file documents, error message: {e} . Return as empty document list."
            )
            return []
        else:
            # Raise the error if it is not the case of empty data dir
            raise e
