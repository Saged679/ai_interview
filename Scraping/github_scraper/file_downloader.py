"""
File downloader — retrieves actual source code from repositories.

Uses the Git Trees API to get the full file tree in a single API call,
then downloads individual file contents via the Blobs API.

Configurable guards:
  - MAX_FILE_SIZE_BYTES: skip files larger than this (default 500 KB)
  - MAX_FILES_PER_REPO: stop after downloading this many files (default 200)
  - Skips binary blobs automatically
"""

import base64
import logging
from typing import Any, Dict, List, Optional

from github_scraper.client import GitHubClient

logger = logging.getLogger("github_scraper.file_downloader")

# ── Configuration ───────────────────────────────────────────────────────
MAX_FILE_SIZE_BYTES = 500 * 1024   # 500 KB
MAX_FILES_PER_REPO = 200

# Common binary extensions to skip outright (saves API calls)
BINARY_EXTENSIONS = frozenset({
    ".png", ".jpg", ".jpeg", ".gif", ".bmp", ".ico", ".svg", ".webp",
    ".mp4", ".mp3", ".wav", ".avi", ".mov", ".flv",
    ".zip", ".tar", ".gz", ".bz2", ".7z", ".rar",
    ".exe", ".dll", ".so", ".dylib", ".o", ".a",
    ".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx",
    ".woff", ".woff2", ".ttf", ".eot", ".otf",
    ".pyc", ".class", ".jar",
    ".db", ".sqlite", ".sqlite3",
    ".DS_Store",
})

# Directories to skip entirely (avoids downloading third-party/generated code)
SKIP_DIRECTORIES = frozenset({
    ".venv", "venv", "env", ".env",
    "node_modules",
    "__pycache__",
    ".git",
    "dist", "build", "out",
    ".tox", ".nox",
    ".eggs", "*.egg-info",
    "vendor",
    ".idea", ".vscode",
    "coverage", ".nyc_output",
    ".cache", ".pytest_cache", ".mypy_cache",
})


def download_repo_files(
    client: GitHubClient,
    owner: str,
    repo_name: str,
    default_branch: str = "main",
    max_file_size: int = MAX_FILE_SIZE_BYTES,
    max_files: int = MAX_FILES_PER_REPO,
) -> List[Dict[str, Any]]:
    """
    Download all text source files from a repository.

    Parameters
    ----------
    client : GitHubClient
        Authenticated API client.
    owner : str
        Repository owner (GitHub username).
    repo_name : str
        Repository name.
    default_branch : str
        Branch to fetch the tree from.
    max_file_size : int
        Maximum file size in bytes to download.
    max_files : int
        Maximum number of files to download per repo.

    Returns
    -------
    list[dict]
        Each dict has keys: ``path``, ``size``, ``content`` (decoded text).
    """
    logger.info(
        "Downloading files for %s/%s (branch=%s, max_size=%dKB, max_files=%d)",
        owner, repo_name, default_branch, max_file_size // 1024, max_files,
    )

    # ── 1. Get the full recursive tree in one API call ──────────────────
    tree_data = client.get(
        f"/repos/{owner}/{repo_name}/git/trees/{default_branch}",
        params={"recursive": "1"},
    )

    if tree_data is None:
        logger.error("Could not fetch file tree for %s/%s.", owner, repo_name)
        return []

    if tree_data.get("truncated"):
        logger.warning(
            "File tree for %s/%s was TRUNCATED by GitHub (repo is very large). "
            "Some files may be missing.",
            owner, repo_name,
        )

    tree_items = tree_data.get("tree", [])
    # Filter to blobs (files) only
    file_items = [item for item in tree_items if item.get("type") == "blob"]
    logger.info("File tree has %d files for %s/%s.", len(file_items), owner, repo_name)

    # ── 2. Filter and download each file ────────────────────────────────
    downloaded_files: List[Dict[str, Any]] = []
    skipped_binary = 0
    skipped_size = 0
    skipped_dir = 0

    for item in file_items:
        if len(downloaded_files) >= max_files:
            logger.warning(
                "Reached max file limit (%d) for %s/%s. Stopping download.",
                max_files, owner, repo_name,
            )
            break

        file_path = item.get("path", "")
        file_size = item.get("size", 0)

        # Skip files inside excluded directories (.venv, node_modules, etc.)
        if _is_in_skipped_dir(file_path):
            skipped_dir += 1
            logger.debug("Skipping file in excluded directory: %s", file_path)
            continue

        # Skip binary files
        if _is_binary(file_path):
            skipped_binary += 1
            logger.debug("Skipping binary file: %s", file_path)
            continue

        # Skip oversized files
        if file_size > max_file_size:
            skipped_size += 1
            logger.debug(
                "Skipping oversized file: %s (%d KB > %d KB limit)",
                file_path, file_size // 1024, max_file_size // 1024,
            )
            continue

        # Download via Blobs API
        content = _download_blob(client, owner, repo_name, item.get("sha"), file_path)
        if content is not None:
            downloaded_files.append({
                "path": file_path,
                "size": file_size,
                "content": content,
            })

    logger.info(
        "Downloaded %d files for %s/%s (skipped: %d excluded-dir, %d binary, %d oversized).",
        len(downloaded_files), owner, repo_name, skipped_dir, skipped_binary, skipped_size,
    )
    return downloaded_files


# ═══════════════════════════════════════════════════════════════════════════
#  Private helpers
# ═══════════════════════════════════════════════════════════════════════════


def _is_in_skipped_dir(path: str) -> bool:
    """Check if the file resides inside a directory that should be skipped."""
    parts = path.split("/")
    return any(part in SKIP_DIRECTORIES for part in parts[:-1])


def _is_binary(path: str) -> bool:
    """Check if a file path looks like a binary file based on its extension."""
    dot_idx = path.rfind(".")
    if dot_idx == -1:
        return False
    ext = path[dot_idx:].lower()
    return ext in BINARY_EXTENSIONS


def _download_blob(
    client: GitHubClient,
    owner: str,
    repo: str,
    sha: str,
    path: str,
) -> Optional[str]:
    """
    Download a single file blob by its SHA.

    Returns decoded text content or None on failure.
    """
    logger.debug("Downloading blob: %s (sha=%s)", path, sha[:8])

    blob_data = client.get(f"/repos/{owner}/{repo}/git/blobs/{sha}")
    if blob_data is None:
        logger.error("Failed to download blob for %s.", path)
        return None

    content = blob_data.get("content", "")
    encoding = blob_data.get("encoding", "")

    if encoding == "base64":
        try:
            decoded = base64.b64decode(content).decode("utf-8", errors="replace")
            return decoded
        except Exception as exc:
            logger.error("Failed to decode blob %s: %s", path, exc)
            return None

    # utf-8 encoding is returned for small files sometimes
    if encoding == "utf-8":
        return content

    logger.warning("Blob %s has unexpected encoding: %s", path, encoding)
    return None
