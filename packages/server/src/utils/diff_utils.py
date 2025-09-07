import difflib
import logging
import os
import re
from typing import Iterator

import aiofiles

from src.model.app.task import DiffFile
from src.utils.git_utils import get_changed_files_from_commit, get_file_content_at_commit

EXCLUDE_FILES = [
    "package-lock.json",
    "yarn.lock",
    "pnpm-lock.yaml",
    "bun.lockb",
    "Gemfile.lock",
    "composer.lock",
    "Pipfile.lock",
    "poetry.lock",
    "*.pyc",
    "*.pyo",
    "__pycache__/",
    ".DS_Store",
    "Thumbs.db",
    "*.o",
    "*.a",
    "*.so",
    "*.dll",
    "*.exe",
    "*.class",
    "*.jar",
    "target/",
    "build/",
    "dist/",
    ".cache/",
    "*.log",
    "*.tmp",
    "*.swp",
    ".idea/",
    "*.iml",
    ".vscode/",
    "*.suo",
    "*.user",
    "venv/",
    "env/",
    "node_modules/",
    ".pytest_cache/",
    ".mypy_cache/",
    ".ruff_cache/",
    "*.egg-info/",
]

DIFF_HEADER_RE = re.compile(r"^diff --git a/(.+?) b/(.+)$")
HUNK_HEADER_RE = re.compile(r"@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@(?: (.*))?")
INDEX_HEADER_RE = re.compile(r"^index\s+\w+\.\.\w+")
MODE_HEADER_RE = re.compile(r"^(new|deleted) file mode \d+$")

logger = logging.getLogger(__name__)


async def generate_diff_files_async(
    repo_directory: str,
    head_commit: str,
    base_commit: str | None,
) -> list[DiffFile]:
    try:
        diff_files = []
        changed_file_paths = get_changed_files_from_commit(repo_directory, head_commit, base_commit)
        for file_path in changed_file_paths:
            old_content = get_file_content_at_commit(repo_directory, file_path, base_commit)

            full_file_path = os.path.join(repo_directory, file_path)
            if os.path.exists(full_file_path):
                try:
                    async with aiofiles.open(full_file_path, mode="r", encoding="utf-8") as file:
                        new_content = await file.read()
                except UnicodeDecodeError as e:
                    logger.error(f"UnicodeDecodeError: Unable to decode file '{full_file_path}': {e}")
            else:
                new_content = ""

            diff_body = generate_diff(old_content, new_content)
            if diff_body.strip():
                diff_files.append(DiffFile(file_path=file_path, body=diff_body))
        return diff_files
    except Exception as e:
        logger.error(f"Failed to generate diff files for commit {head_commit}: {e}")
        raise


def generate_diff(from_file: str, to_file: str) -> str:
    # split with keepends to preserve multiple newlines, then strip each line
    from_lines = [line.rstrip("\n") for line in from_file.splitlines(keepends=True)]
    to_lines = [line.rstrip("\n") for line in to_file.splitlines(keepends=True)]
    diff_lines = difflib.unified_diff(
        from_lines,
        to_lines,
        lineterm="",
        n=len(from_lines) + len(to_lines),
    )
    return "\n".join(_filter_lines(diff_lines))


def _filter_lines(diff_lines: Iterator[str]) -> list[str]:
    lines = []
    for line in diff_lines:
        if _is_header_line(line):
            continue
        if line.startswith(" "):
            line = line[1:]
        lines.append(line)
    return lines


def _is_header_line(line: str) -> bool:
    """
    Check if a line is a git diff header line that should be excluded from the diff body
    """
    return (
        INDEX_HEADER_RE.match(line) is not None
        or HUNK_HEADER_RE.match(line) is not None
        or MODE_HEADER_RE.match(line) is not None
        or line.startswith("--- ")
        or line.startswith("+++ ")
    )
