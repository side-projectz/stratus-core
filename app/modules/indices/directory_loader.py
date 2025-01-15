from app.utils import logger
from app.utils.git import exclude_ignored_documents


def load_documents(path: str):
	from llama_index.core.readers import SimpleDirectoryReader

	try:
		import nest_asyncio

		nest_asyncio.apply()

		exclude_list = [
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
		]

		loader = SimpleDirectoryReader(
			recursive=True,
			filename_as_id=True,
			raise_on_error=True,
			input_dir=path,
			exclude_hidden=True,
			exclude=exclude_list,
		)
		documents = loader.load_data()

		filtered_docs = exclude_ignored_documents(directory=path, documents=documents)

		for doc in filtered_docs:
			content = doc.text
			metadata = (
				f"""[{doc.metadata['file_name']}]( {doc.metadata['file_path']} ) \n"""
			)
			doc.set_content(metadata + content)

		return filtered_docs

	except Exception as e:
		import sys
		import traceback

		# Catch the error if the data dir is empty
		# and return as empty document list
		_, _, exc_traceback = sys.exc_info()
		function_name = traceback.extract_tb(exc_traceback)[-1].name
		if function_name == "_add_files":
			logger.warning(f"Failed to load file documents, error message: {e}")
			return []
		else:
			# Raise the error if it is not the case of empty data dir
			raise e
