from git import Repo
from git.exc import InvalidGitRepositoryError, NoSuchPathError


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
