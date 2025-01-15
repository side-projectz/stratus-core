from pathlib import Path

from git import Repo
from git.exc import InvalidGitRepositoryError, NoSuchPathError
from llama_index.core import Document
from pathspec import PathSpec
from pathspec.patterns.gitwildmatch import GitWildMatchPattern


def is_git_repo(directory: str):
	try:
		repo = Repo(directory)
		return {
			"is_bare": repo.bare,
			"active_branch": repo.active_branch.name if not repo.bare else None,
			"remote_url": repo.remotes.origin.url if repo.remotes else None,
		}
	except (InvalidGitRepositoryError, NoSuchPathError):
		raise ValueError("Directory is not a valid git repository.")
	except Exception:
		return None


def load_gitignore_patterns(directory: str) -> PathSpec:
	# Path to the .gitignore file
	gitignore_path = Path(directory) / ".gitignore"
	if not gitignore_path.exists():
		# If there’s no .gitignore, create an empty PathSpec (matches nothing)
		return PathSpec.from_lines(GitWildMatchPattern, [])

	with gitignore_path.open("r") as f:
		lines = f.read().splitlines()
	# PathSpec automatically ignores blank and comment lines
	return PathSpec.from_lines(GitWildMatchPattern, lines)


def exclude_ignored_documents(
	directory: str, documents: list[Document]
) -> list[Document]:
	"""
	Return documents that are **not** matched by `.gitignore`
	(i.e., the "included" documents).
	"""
	spec = load_gitignore_patterns(directory)

	included_docs = []
	for doc in documents:
		doc_path = str(doc.metadata["file_path"]).replace(directory, "")
		if not spec.match_file(doc_path):
			included_docs.append(doc)

	return included_docs
