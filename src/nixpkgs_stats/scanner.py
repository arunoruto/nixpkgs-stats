import os
from pathlib import Path

from git import InvalidGitRepositoryError, Repo


def get_repo_info(repo_path: str) -> dict[str, str] | None:
    try:
        repo = Repo(repo_path, search_parent_directories=False)
    except InvalidGitRepositoryError:
        return None

    head = repo.head.commit
    return {
        "hash": head.hexsha[:7],
        "date": head.committed_datetime.strftime("%Y-%m-%d"),
    }


def scan(
    repo_path: str, mode: str = "directories", exclude_lib: bool = False
) -> dict[str, int]:
    by_name = Path(repo_path) / "pkgs" / "by-name"

    if not by_name.is_dir():
        msg = f"'pkgs/by-name/' not found inside '{repo_path}'"
        raise FileNotFoundError(msg)

    counts: dict[str, int] = {}

    for prefix_dir in sorted(by_name.iterdir()):
        if not prefix_dir.is_dir():
            continue

        prefix = prefix_dir.name
        if len(prefix) != 2 or not prefix.isalpha():
            continue

        prefix_lower = prefix.lower()

        if mode == "files":
            count = 0
            for _dirpath, _dirnames, filenames in os.walk(prefix_dir):
                rel = os.path.relpath(_dirpath, prefix_dir)
                pkg_name = rel.split(os.sep)[0] if rel != "." else ""
                if (
                    exclude_lib
                    and prefix_lower == "li"
                    and pkg_name.lower().startswith("lib")
                ):
                    continue
                count += sum(1 for f in filenames if f.endswith(".nix"))
        else:
            subdirs = [
                child
                for child in prefix_dir.iterdir()
                if child.is_dir() and any(child.glob("*.nix"))
            ]
            if exclude_lib and prefix_lower == "li":
                subdirs = [d for d in subdirs if not d.name.lower().startswith("lib")]
            count = len(subdirs)

        counts[prefix_lower] = counts.get(prefix_lower, 0) + count

    return counts
