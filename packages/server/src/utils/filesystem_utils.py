import asyncio
import os
import shutil
from pathlib import Path

IGNORE_PATTERNS = {
    ".git",
    "__pycache__",
    "node_modules",
    ".venv",
    ".env",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    "dist",
    "build",
    ".DS_Store",
    "Thumbs.db",
    ".vscode",
    ".idea",
    "*.pyc",
    "*.pyo",
    "*.pyd",
    ".coverage",
    "coverage.xml",
    "*.log",
    ".tmp",
    "tmp",
}


async def create_directory_async(directory_path: str):
    assert directory_path.startswith("/tmp/async/")
    await asyncio.to_thread(os.makedirs, directory_path)


async def cleanup_directory_async(directory_path: str | None):
    if not directory_path or not os.path.exists(directory_path):
        return
    await asyncio.to_thread(shutil.rmtree, directory_path)


async def generate_project_tree_async(repo_directory: str) -> str:
    if not repo_directory or not os.path.exists(repo_directory) or not os.path.isdir(repo_directory):
        raise ValueError(f"Repository is not cloned: {repo_directory}")
    return await asyncio.to_thread(_generate_project_tree, repo_directory)


def _generate_project_tree(repo_directory: str) -> str:
    repo_dir = Path(repo_directory)
    lines = [repo_dir.name]
    lines.extend(_build_tree_structure(repo_dir))
    return "\n".join(lines)


def _build_tree_structure(directory: Path, prefix: str = "", is_last: bool = True) -> list[str]:
    lines = []
    items = sorted(directory.iterdir(), key=lambda p: (p.is_file(), p.name.lower()))
    items = [item for item in items if not _should_ignore(item)]
    for i, item in enumerate(items):
        is_last_item = i == len(items) - 1

        if is_last_item:
            current_prefix = "└── "
            next_prefix = prefix + "    "
        else:
            current_prefix = "├── "
            next_prefix = prefix + "│   "

        lines.append(f"{prefix}{current_prefix}{item.name}")
        if item.is_dir():
            lines.extend(_build_tree_structure(item, next_prefix, is_last_item))
    return lines


def _should_ignore(path: Path) -> bool:
    return path.name in IGNORE_PATTERNS or path.name.startswith(".")
